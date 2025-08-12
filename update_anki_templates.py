#!/usr/bin/env python3
"""Update Anki note type templates to include audio on the back"""

import requests
import json

def update_anki_templates():
    """Update the Fluent Forever note type templates"""
    
    # AnkiConnect URL
    anki_url = "http://localhost:8765"
    
    # Template data with audio added to back
    templates = [
        {
            "Name": "Comprehension (Audio + Image + Gapped)",
            "Front": """
<div class="card-front">
  <!-- Audio controls -->
  <div class="audio-controls">
    {{WordAudio}}
    {{#WordAudioAlt}}<br>{{WordAudioAlt}}{{/WordAudioAlt}}
  </div>
  
  <!-- Main image -->
  <div class="image-container">
    {{#ImageFile}}<img src="{{ImageFile}}">{{/ImageFile}}
  </div>
  
  <!-- Spanish definition -->
  <div class="definition">
    {{MonolingualDef}}
  </div>
  
  <!-- Gapped sentence for comprehension -->
  {{#GappedSentence}}
  <div class="gapped-sentence">
    {{GappedSentence}}
  </div>
  {{/GappedSentence}}
  
  <!-- Context hint -->
  {{#MeaningContext}}
  <div class="context-hint">
    ({{MeaningContext}})
  </div>
  {{/MeaningContext}}
</div>
""",
            "Back": """
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
  
  <!-- Full example sentence -->
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
  
  <!-- Personal memory aid -->
  {{#PersonalMnemonic}}
  <div class="mnemonic">
    💭 {{PersonalMnemonic}}
  </div>
  {{/PersonalMnemonic}}
</div>
"""
        },
        {
            "Name": "Recall (Image + Definition Only)",
            "Front": """
<div class="card-front">
  <!-- Main image only -->
  <div class="image-container">
    {{#ImageFile}}<img src="{{ImageFile}}">{{/ImageFile}}
  </div>
  
  <!-- Spanish definition only -->
  <div class="definition">
    {{MonolingualDef}}
  </div>
  
  <!-- Context hint -->
  {{#MeaningContext}}
  <div class="context-hint">
    ({{MeaningContext}})
  </div>
  {{/MeaningContext}}
</div>
""",
            "Back": """
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
        }
    ]
    
    # Update templates
    payload = {
        "action": "updateModelTemplates",
        "version": 6,
        "params": {
            "model": {
                "name": "Fluent Forever",
                "templates": templates
            }
        }
    }
    
    try:
        response = requests.post(anki_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")  # Debug line
            if isinstance(result, dict) and result.get("error"):
                print(f"Error: {result['error']}")
                return False
            else:
                print("✅ Successfully updated Anki templates to include audio on the back")
                return True
        else:
            print(f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error updating templates: {e}")
        return False

if __name__ == "__main__":
    update_anki_templates()