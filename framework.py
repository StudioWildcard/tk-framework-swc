# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk,os

logger = sgtk.platform.get_logger(__name__)

class SwcFramework(sgtk.platform.Framework):
    def init_framework(self):
        """
        Implemented by deriving classes in order to initialize the app.
        Called by the engine as it loads the framework.
        """
        self.log_debug("%s: Initializing..." % self)


    def destroy_framework(self):
        """
        Implemented by deriving classes in order to tear down the framework.
        Called by the engine as it is being destroyed.
        """
        self.log_debug("%s: Destroying..." % self)

    def find_task_context(self, path):
        # Try to get the context more specifically from the path on disk
        tk = sgtk.sgtk_from_path( path )
        context = tk.context_from_path(path)

        # In case the task folder is not registered for some reason, we can try to find it
        if not context.task:
            # This is either an Asset root or an Animation
            if not context.step:
                context_entity = context.sgtk.shotgun.find_one(context.entity["type"],
                                                               [["id", "is", context.entity["id"]]],
                                                               ["sg_asset_parent","sg_asset_type"])
                # Must be an animation...
                if context_entity.get("sg_asset_type") == "Animations":
                    file_name = os.path.splitext(os.path.basename(path))[0]
                    # SWC JR: This could get slow if there are a lot of tasks, not sure if there is a way to query instead            
                    tasks = context.sgtk.shotgun.find("Task", [["entity", "is", context.entity]], ['content'])
                    match_length = len(file_name)
                    new_context_id = None
                    for task in tasks:                        
                        task_content = task['content']
                        new_length = len(file_name) - len(task_content)
                        if task_content in file_name and new_length < match_length:
                            # We found a matching task
                            new_context_id = task['id']
                            # This is the new best task
                            match_length = new_length
                    
                    if new_context_id:
                        context = tk.context_from_entity("Task", new_context_id)
            if context.step:
                file_folder = os.path.basename(os.path.dirname(path))
                context_task = context.sgtk.shotgun.find_one("Task", [["content", "is", file_folder],["entity", "is", context.entity],["step", "is", context.step]])
                if context_task:
                    context = tk.context_from_entity("Task", context_task["id"])
        return context
