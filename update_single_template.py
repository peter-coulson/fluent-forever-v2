#!/usr/bin/env python3
"""Update a single Anki template to include audio on the back"""

import requests
import json

def update_recall_template():
    """Update just the Recall template back side"""
    
    anki_url = "http://localhost:8765"
    
    # New back template with audio
    back_template = """
<div class="card-back">
  <!-- Front side -->
  {{FrontSide}}
  
  <hr id="answer">
  
  <!-- Word and pronunciation with ENHANCED IPA -->
  <div class="word-main">
    <span class="spanish">{{SpanishWord}}</span>
    {{#IPA}}<span class="ipa">{{IPA}}</span>{{/IPA}}
  </div>
  
  <!-- Audio on back -->
  <div class="audio-back">
    {{WordAudio}}
    {{#WordAudioAlt}}{{WordAudioAlt}}{{/WordAudioAlt}}
  </div>
  
  <!-- Meaning context -->
  {{#MeaningContext}}
  <div class="meaning-context">
    {{MeaningContext}}
  </div>
  {{/MeaningContext}}
  
  <!-- Example sentence for context -->
  {{#ExampleSentence}}
  <div class="examples">
    <div class="full-sentence">{{ExampleSentence}}</div>
  </div>
  {{/ExampleSentence}}
  
  <!-- Usage notes -->
  {{#UsageNote}}
  <div class="usage-note">
    📝 {{UsageNote}}
  </div>
  {{/UsageNote}}
</div>
"""
    
    # Update the specific template
    payload = {
        "action": "updateModelTemplates",
        "version": 6,
        "params": {
            "model": {
                "name": "Fluent Forever",
                "templates": {
                    "Recall (Image + Definition Only)": {
                        "Back": back_template
                    }
                }
            }
        }
    }
    
    try:
        response = requests.post(anki_url, json=payload)
        result = response.json()
        print(f"Full response: {result}")
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        else:
            print("✅ Successfully updated Recall template")
            return True
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    update_recall_template()