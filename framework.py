# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk,os,re

logger = sgtk.platform.get_logger(__name__)

# import ptvsd

# # Allow other computers to attach to ptvsd at this IP address and port.
# ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)

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

        if not context:
            self.log_debug(f"{path} does not correspond to any context!")
            return None
            
        # In case the task folder is not registered for some reason, we can try to find it
        if not context.task:
            # Publishing Asset
            if context.entity["type"] == "CustomEntity03":
                # We can only hope to match this file if it already is in a Step folder
                if context.step:
                    file_name = os.path.splitext(os.path.basename(path))[0]
                    # Get all the possible tasks for this Asset Step 
                    context_tasks = context.sgtk.shotgun.find("Task", [["entity", "is", context.entity],["step", "is", context.step]], ["content"])
                    for context_task in context_tasks:                        
                        # Build the regex pattern using https://regex101.com/r/uK8Ca4/1
                        task_name = context_task.get("content")
                        regex = r"\S*(" + re.escape(task_name) + r"){1}(?:_\w*)?$"
                        matches = re.finditer(regex, file_name)
                        for matchNum, match in enumerate(matches, start=1):
                            for group in match.groups():
                                # Assuming there is only ever one match since the match is at the end of the string
                                if group == task_name:
                                    return tk.context_from_entity("Task", context_task["id"])                     
            # Cinematics
            elif context.entity["type"] == "Sequence" or context.entity["type"] == "Shot":
                if context.step:
                    return self._find_context(tk,context,path)
            # All other entities
            else:
                # This is either an Asset root or an Animation
                if not context.step:
                    context_entity = context.sgtk.shotgun.find_one(context.entity["type"],
                                                                [["id", "is", context.entity["id"]]],
                                                                ["sg_asset_parent","sg_asset_type"])
                    # Must be an animation...
                    if context_entity.get("sg_asset_type") == "Animations":
                        return self._find_context(tk,context,path)

                elif context.step['name'] == "Animations":
                    return self._find_context(tk,context,path)

                elif context.step['name'] != "Animations":
                    file_folder = os.path.basename(os.path.dirname(path))
                    context_task = context.sgtk.shotgun.find_one("Task", [["content", "is", file_folder],["entity", "is", context.entity],["step", "is", context.step]])
                    if context_task:
                        return tk.context_from_entity("Task", context_task["id"])
        
        return context

    def _find_context(self, tk, context, path):
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
        
        return context     
