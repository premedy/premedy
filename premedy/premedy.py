import logging
from os import listdir
from os.path import isfile, join

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
        )(self.consume_handler)

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

            module = __import__(f"{import_path}.{file_without_extension}")

            for sub_module in import_path.split(".")[1:]:
                module = getattr(module, sub_module)

            module = getattr(module, file_without_extension)

            klass = getattr(module, klass_name)

            self.remediation_classes.append(klass)

    def consume_handler(self, message):
        finding_result = findings.parse_finding_result(message=message)
        self.remediate(finding_result=finding_result)
        return {}

    def remediate(self, finding_result):
        saved_finding = False

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
                    findings.save_in_gcs_bucket(
                        finding_result=finding_result,
                        store_path_handler=path_handler_action_taken,
                    )
                    saved_finding = True
                except:
                    self.app.log.error(f" Could not remediate: {instance.__class__}")
                    findings.save_in_gcs_bucket(
                        finding_result=finding_result,
                        store_path_handler=path_handler_error_while_taking_action,
                    )
                    saved_finding = True
            else:
                if not saved_finding:
                    findings.save_in_gcs_bucket(
                        finding_result=finding_result,
                        store_path_handler=path_handler_no_remediation_for_finding,
                    )


def path_handler_action_taken(finding_result):
    default_path = findings.default_store_path_handler(finding_result)
    return f"action_taken/f{default_path}"


def path_handler_error_while_taking_action(finding_result):
    default_path = findings.default_store_path_handler(finding_result)
    return f"error_while_taking_action/f{default_path}"


def path_handler_no_remediation_for_finding(finding_result):
    default_path = findings.default_store_path_handler(finding_result)
    return f"no_remediation_for_finding/f{default_path}"
