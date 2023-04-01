import logging
import sys
from glob import glob
from os import listdir
from os.path import isfile, join
from pydoc import locate

from premedy import config
from premedy.resources import findings

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


class Premedy:
    def __init__(self, app, topic, project, path, use_subscription=True):
        self.app = app
        self.topic = topic
        self.project = project
        self.use_subscription = use_subscription
        self.remediation_classes = []
        self.path = path
        self.load_remediation_classes()
        self.consume = self.app.topic(
            topic=self.topic,
            project=self.project,
            use_subscription=self.use_subscription,
        )(self.consume)

    @staticmethod
    def to_camel_case(snake_str):
        components = snake_str.split("_")
        return "".join(x.title() for x in components)

    def load_remediation_classes(self):
        file_names = [f for f in listdir(self.path) if isfile(join(self.path, f))]

        for file_name in file_names:
            if file_name == "__init__.py":
                continue

            file_without_extension = file_name.split(".")[0]
            klass_name = f"Remediate{self.to_camel_case(file_without_extension)}"

            import_path = ".".join(self.path.replace("./", "").split("/"))

            imported_module = __import__(f"{import_path}.{file_without_extension}")

            module = imported_module
            for sub_module in import_path.split(".")[1:]:
                module = getattr(module, sub_module)

            module = getattr(module, file_without_extension)

            klass = getattr(module, klass_name)

            self.remediation_classes.append(klass)

    def load_remediation_classes_deprecated(self):
        sys.path.append(self.path)
        remediation_classes = []

        for file in glob(f"{self.path}/*.py"):
            if file.endswith("__init__.py"):
                continue

            logger.debug(f"loading: {file}")
            with open(file, "r") as f:
                line = ""
                while "class" not in line and "(RemediationBase)" not in line:
                    line = f.readline()
            class_name = (
                line.strip()
                .replace("(RemediationBase):", "")
                .replace("class ", "")
                .strip()
            )
            module_name = (
                file.replace("./", "")
                .replace(".py", "")
                .replace("/", ".")
                .split(".")[-1]
            )
            remediation_class = locate(f"{module_name}.{class_name}")
            if not remediation_class:
                logger.error(f"failed to load {file}")
                continue

            remediation_classes.append(remediation_class)
            logger.debug(f"loaded: class {class_name} from {file}")

        self.remediation_classes = remediation_classes

    def consume(self, message):
        finding_result = findings.parse_finding_result(message=message)
        findings.save_in_gcs_bucket(finding_result=finding_result)
        self.remediate(finding_result=finding_result)
        return {}

    def remediate(self, finding_result):
        for remediation in self.remediation_classes:
            instance = remediation(finding_result=finding_result)
            self.app.log.info(f" Check Remediation Class {instance.__class__}")
            if instance.should_take_action():
                try:
                    self.app.log.info(
                        f" Take Action Remediation Class {instance.__class__}"
                    )
                    response = instance.remediate()
                    self.app.log.info(
                        f" Action Response Remediation Class {instance.__class__}: {response}"
                    )
                except:
                    self.app.log.error(f" Could not remediate: {instance.__class__}")
