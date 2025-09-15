#!/usr/bin/env python
"""Review the generated Django models"""

def review_generated_models():
    """Read and display summary of generated models"""
    try:
        with open('generated_models.py', 'r') as f:
            content = f.read()
        
        print("📋 GENERATED MODELS SUMMARY")
        print("=" * 50)
        
        # Count models
        model_lines = [line for line in content.split('\n') if line.startswith('class ')]
        
        print(f"✅ Generated {len(model_lines)} Django models")
        print("\n📝 Model Classes:")
        
        for line in model_lines:
            class_name = line.split('class ')[1].split('(')[0]
            print(f"  • {class_name}")
        
        print(f"\n📁 File size: {len(content):,} characters")
        print("📍 Location: generated_models.py")
        
        print(f"\n🔍 First few models preview:")
        lines = content.split('\n')
        preview_lines = []
        in_model = False
        model_count = 0
        
        for line in lines:
            if line.startswith('class ') and model_count < 3:
                in_model = True
                model_count += 1
                preview_lines.append(line)
            elif in_model and (line.startswith('class ') or line.strip() == ''):
                if line.startswith('class '):
                    break
                in_model = False
                preview_lines.append('')
            elif in_model:
                preview_lines.append(line)
        
        for line in preview_lines:
            print(line)
        
        if len(model_lines) > 3:
            print(f"\n... and {len(model_lines) - 3} more models")
        
        return True
        
    except FileNotFoundError:
        print("❌ generated_models.py file not found")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    review_generated_models()