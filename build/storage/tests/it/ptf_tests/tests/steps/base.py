# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.test_platform import BaseTestPlatform


class TestStep:
    """The base class represents the single step in test story
    It's abstract class
    """

    def __init__(self, platform: BaseTestPlatform, is_teardown: bool = False) -> None:
        self.platform = platform
        self.is_teardown = is_teardown
        self.result = {}

    def _prepare(self):
        pass

    def _assertions_before_step(self):
        pass

    def _step(self):
        pass

    def _assertion_after_step(self):
        pass

    def _teardown(self):
        pass

    def run(self):
        """This is the only public method in step

        This method represents what you have to do if you want properly validate one step in test story.
        First, you have to prepare environment. Second, check if all preconditions are fulfilled.
        Next is action and check if postconditions is fulfilled. The last is bringing environment to beggining.

        If you initialize class with is_teardown=False the environment after step not will be bringing to beggining.
        It is allow connect steps with whole test story.
        You have to remember to yourself teardown environment after all steps.
        """
        self._prepare()
        self._assertions_before_step()
        self._step()
        self._assertion_after_step()
        if self.is_teardown:
            self._teardown()
        return self.result
