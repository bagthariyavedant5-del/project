def get_symptoms_for_stage(stage_index):
    # Mapping retina signs/stages to possible symptoms
    symptoms_map = {
        0: [], # No DR
        1: ["Mild blurred vision (rare)"], # Mild
        2: ["Blurred vision", "Dark spots (floaters)"], # Moderate
        3: ["Blurred vision", "Dark spots (floaters)", "Impaired color vision", "Night vision problems"], # Severe
        4: ["Severe blurred vision", "Vision loss", "Significantly impaired night vision", "Empty/dark areas in vision"] # Proliferative
    }
    
    return symptoms_map.get(stage_index, [])
