import sgtk,os,re
logger = sgtk.platform.get_logger(__name__)

# Define some inactive task states for inferring context
inactive_task_states = ['wtg', 'apr', 'fin']

def find_task_context(path):
    # Try to get the context more specifically from the path on disk
    context = None
    try:
        tk = sgtk.sgtk_from_path( path )
        context = tk.context_from_path(path)
    except Exception as e:
        logger.debug(f"Error: {e}")

    if not context:
        logger.debug(f"{path} does not correspond to any context!")
        return None
        
    # In case the task folder is not registered for some reason, we can try to find it
    if not context.task:
        # Publishing Asset
        if context.entity["type"] == "CustomEntity03":
            # We can only hope to match this file if it already is in a Step folder
            # if context.step:
            file_name = os.path.splitext(os.path.basename(path))[0]
            # Get all the possible tasks for this Asset Step 
            context_tasks = context.sgtk.shotgun.find("Task", [["entity", "is", context.entity]], ["content"])
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
                return _find_context(tk,context,path)
        # All other entities
        else:
            # This is either an Asset root or an Animation
            if not context.step:
                context_entity = context.sgtk.shotgun.find_one(context.entity["type"],
                                                            [["id", "is", context.entity["id"]]],
                                                            ["sg_asset_parent","sg_asset_type"])
                # Must be an animation...
                if context_entity.get("sg_asset_type") == "Animations":
                    return _find_context(tk,context,path)

            elif context.step['name'] == "Animations":
                return _find_context(tk,context,path)

            elif context.step['name'] != "Animations":
                # file_folder = os.path.basename(os.path.dirname(path))
                step_tasks = context.sgtk.shotgun.find("Task", [["entity", "is", context.entity],["step", "is", context.step]], ['content', 'step', 'sg_status_list'])
                step_tasks_list = [task for task in step_tasks if task['step'] == context.step]
                if len(step_tasks_list) == 1:
                    return tk.context_from_entity("Task", step_tasks_list[0]["id"])
                else:
                    active_tasks = [task for task in step_tasks if task['sg_status_list'] not in inactive_task_states] #context.sgtk.shotgun.find_one("Task", [["content", "is", file_folder],["entity", "is", context.entity],["step", "is", context.step]])
                    if len(active_tasks) == 1:
                        return tk.context_from_entity("Task", active_tasks[0]["id"])
                        # TODO: Add a check for tasks belonging to the current user if this still doesn't narrow it down
    
    return context

def _find_context(tk, context, path):
    file_name = os.path.splitext(os.path.basename(path))[0]
    # SWC JR: This could get slow if there are a lot of tasks, not sure if there is a way to query instead        
    if context.step:    
        tasks = [x for x in context.sgtk.shotgun.find("Task", [["entity", "is", context.entity],["step", "is", context.step]], ['content']) if f"_{x['content']}" in file_name]
    else:    
        tasks = [x for x in context.sgtk.shotgun.find("Task", [["entity", "is", context.entity]], ['content']) if f"_{x['content']}" in file_name]

    match_length = len(file_name)
    new_context_id = None

    for task in tasks:
        new_length = len(file_name) - len(task['content'])
        if new_length < match_length:
            # We found a matching task
            new_context_id = task['id']
            # This is the new best task
            match_length = new_length
    
    if new_context_id:
        context = tk.context_from_entity("Task", new_context_id)
    
    return context     