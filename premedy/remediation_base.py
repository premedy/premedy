import traceback

from premedy import config
from google.cloud.securitycenter_v1 import ListFindingsResponse
import functools
from google.cloud import asset_v1
import re
import logging
from premedy.resources import slack


logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


class RemediationBase:
    category = None
    remediation_functions = {}
    _asset = None

    def __init__(self, finding_result: ListFindingsResponse.ListFindingsResult):
        self.finding_result = finding_result
        self.logger = logger
        if self.category is None:
            raise Exception("missing category: set a category in the child instance")

    @classmethod
    def remediation(cls, notify_success=False, notify_error=True):
        def wrapper(func):
            """Decorator. Stores function in an array. Arrays are indexed by class"""
            class_name, function_name = func.__qualname__.split(".")
            if class_name not in cls.remediation_functions:
                cls.remediation_functions[class_name] = []
            cls.remediation_functions[class_name].append(
                {
                    "name": function_name,
                    "notify_success": notify_success,
                    "notify_error": notify_error,
                }
            )
            return func

        if type(notify_success).__name__ == "function":
            _func = notify_success
            notify_success = False
            return wrapper(_func)
        else:
            return wrapper

    def remediate(self):
        def notify_success(class_name, function_name, response):
            message = f"ran {class_name}.{function_name}. returned {response} :smile:"
            slack.send_message(message=message)
            logger.debug(message)

        def notify_error(class_name, function_name, stack_trace):
            message = f"error running {class_name}.{function_name}.\n{stack_trace} :melting_face:"
            slack.send_message(message=message)
            logger.debug(message)

        class_name = self.__class__.__name__
        for function in self.__class__.remediation_functions[class_name]:
            function_name = function["name"]
            try:
                func = getattr(self, function_name)
                response = func()
                if function["notify_success"]:
                    notify_success(class_name, function_name, response)
            except Exception as e:
                logger.error(f"executing: {function_name}: {str(e)}")

                if function["notify_error"]:
                    notify_error(class_name, function_name, traceback.format_exc())

    @property
    def project(self):
        return self.finding_result.resource.project_display_name

    @property
    def region(self):
        if "/regions/" in self.finding_result.resource.name:
            return self.finding_result.resource.name.split("/")[-3]
        return None

    @property
    def asset(self):
        if not self._asset:
            project_resource = "projects/{}".format(self.project)
            client = asset_v1.AssetServiceClient()
            resource_name = self.finding_result.resource.name
            # Call ListAssets v1 to list assets.
            request = {"scope": project_resource, "query": f"name:{resource_name}"}
            logger.debug(f"fetch asset: {resource_name}")
            response = client.search_all_resources(request=request)
            asset: asset_v1.ResourceSearchResult = response.results[0]
            logger.debug(asset)
            self._asset = asset
        return self._asset

    def project_filter(project: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self):
                if project == self.project:
                    logger.debug(f"project filter match: {project}")
                    return func(self)

            return wrapper

        return decorator

    def resource_name_filter(regexp: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self):
                resource_name = self.finding_result.resource.display_name.split("/")[0]
                regexp_result = re.findall(regexp, resource_name)
                if regexp_result:
                    logger.debug(
                        f"resource name filter match: {regexp_result} for {regexp} in {resource_name}"
                    )
                    return func(self)
                else:
                    logger.debug(f"no match for {regexp} in {resource_name}")

            return wrapper

        return decorator

    def region_filter(region: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self):
                if region == self.region:
                    logger.debug(f"region filter match: {region}")
                    return func(self)

            return wrapper

        return decorator

    def folder_filter(folder: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self):
                for resource_folder in self.finding_result.resource.folders:
                    if folder == resource_folder.resource_folder_display_name:
                        logger.debug(f"folder filter match: {folder}")
                        return func(self)

            return wrapper

        return decorator

    def label_filter(labels: dict):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self):
                for label_key, label_value in labels.items():
                    try:
                        if not self.asset.labels[label_key] == label_value:
                            return
                        logger.debug(
                            f"label filter match: {label_key} -> {label_value}"
                        )

                    except Exception as e:
                        return

                return func(self)

            return wrapper

        return decorator

    def should_take_action(self) -> bool:
        if self.finding_result.finding.category != self.category:
            return False

        logger.debug(f"category match: {self.category}")
        return True


remediation = RemediationBase.remediation
region_filter = RemediationBase.region_filter
label_filter = RemediationBase.label_filter
project_filter = RemediationBase.project_filter
resource_name_filter = RemediationBase.resource_name_filter
folder_filter = RemediationBase.folder_filter
