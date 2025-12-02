# --- This was vibe coded with Gemini because my initial workflow could no longer be found. ---
# --- Tyler Dockery --- #

import os
import torch

class PromptBatchIterator:
    def __init__(self):
        # We use a state dictionary to maintain the current index across executions
        # In a real ComfyUI custom node setup, state management usually happens
        # either globally or via shared memory/disk, but for this simple iterator,
        # we'll use a class attribute assuming the ComfyUI session is stable.
        # NOTE: ComfyUI typically handles state on its own, but we define an internal state for clarity.
        self.state = {"index": 0, "prompts": None, "prompt_path": None}

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt_file": ("STRING", {"multiline": False, "default": r"C:\AI\BatchImages\prompts\prompts.txt"}),
                "reset_on_file_change": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "execute_signal": ("*",) # Takes a signal from the Save Image node
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "BOOLEAN") # Current Prompt, Current Index, Total Prompts, Continue/Stop Signal
    RETURN_NAMES = ("CURRENT_PROMPT", "INDEX", "TOTAL_PROMPTS", "CONTINUE_LOOP")
    FUNCTION = "iterate_prompts"
    CATEGORY = "batch_tools" # You can find this node under 'batch_tools'

    def load_prompts(self, prompt_file):
        """Loads and splits the prompt file."""
        if not os.path.exists(prompt_file):
            print(f"Error: Prompt file not found at {prompt_file}")
            return []
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by newline and filter out any empty lines
        prompts = [p.strip() for p in content.split('\n') if p.strip()]
        return prompts

    def iterate_prompts(self, prompt_file, reset_on_file_change, execute_signal=None):
        
        # --- 1. Load/Reload Logic ---
        # Check if the file path has changed or if it's the first run
        file_changed = prompt_file != self.state["prompt_path"]
        
        if self.state["prompts"] is None or file_changed:
            self.state["prompts"] = self.load_prompts(prompt_file)
            self.state["prompt_path"] = prompt_file
            if reset_on_file_change:
                self.state["index"] = 0
                print(f"Loaded {len(self.state['prompts'])} prompts from {prompt_file}. Index reset to 0.")

        prompts = self.state["prompts"]
        total_prompts = len(prompts)
        current_index = self.state["index"]

        # --- 2. Check for Completion ---
        if current_index >= total_prompts:
            print(f"Batch iteration complete. Final index: {current_index}. Total prompts: {total_prompts}.")
            # Reset index for next manual run if needed
            self.state["index"] = 0 
            # Output signals: Empty string, Final index, Total, STOP (False)
            return ("", current_index, total_prompts, False)

        # --- 3. Execute Current Step ---
        current_prompt = prompts[current_index]
        print(f"Executing Prompt {current_index + 1}/{total_prompts}: {current_prompt[:60]}...")
        
        # --- 4. Prepare for Next Step (Increment) ---
        # Crucial: Increment the index for the next execution
        self.state["index"] += 1
        
        # Output signals: Current prompt, Current Index, Total, CONTINUE (True)
        return (current_prompt, current_index, total_prompts, True)

# A standard registration map is needed for ComfyUI
NODE_CLASS_MAPPINGS = {
    "PromptBatchIterator": PromptBatchIterator
}

# Optional: Define user-friendly display names
NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptBatchIterator": "Batch Prompt Iterator"
}
