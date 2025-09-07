#!/usr/bin/env python3
"""
Test Enhanced Intelligent Author System
Validates fixes for poor results and text artifacts
"""

import sys
sys.path.insert(0, 'core_system')

from enhanced_intelligent_author import generate_intelligent_book

def test_enhanced_system():
    """Test the enhanced system fixes"""
    
    print("🧪 TESTING ENHANCED INTELLIGENT AUTHOR")
    print("=" * 50)
    print("Testing fixes for:")
    print("❌ Poor results, nonsense prompts")
    print("❌ Text artifacts in cover images") 
    print("❌ Bullshit content generation")
    print()
    
    # Generate test book
    print("🎨 Generating test book...")
    book = generate_intelligent_book(8)
    
    print(f"✅ Generated: {book['title']}")
    print(f"✅ Categories: {book['categories']}")
    print(f"✅ Total Pages: {book['total_pages']}")
    print(f"✅ Unique ID: {book['unique_id']}")
    print()
    
    # Validate cover prompt (should have NO text elements)
    print("🔍 VALIDATING COVER PROMPT:")
    cover_prompt = book['prompts'][0]['enhanced_prompt']
    cover_negative = book['prompts'][0]['negative_prompt']
    
    print("Cover Prompt:")
    print(f"   {cover_prompt}")
    print()
    
    # Check for text-prevention elements
    text_prevention = [
        "no text elements" in cover_prompt.lower(),
        "no letters" in cover_prompt.lower(), 
        "no words" in cover_prompt.lower(),
        "illustration only" in cover_prompt.lower()
    ]
    
    print("✅ Text Prevention Checks:")
    for i, check in enumerate(text_prevention):
        status = "✅ PASS" if check else "❌ FAIL"
        checks = ["no text elements", "no letters", "no words", "illustration only"]
        print(f"   {status}: {checks[i]} present")
    
    print()
    
    # Validate content prompts
    print("🔍 VALIDATING CONTENT PROMPTS:")
    content_prompt = book['prompts'][1]['enhanced_prompt']
    print("Sample Content Prompt:")
    print(f"   {content_prompt}")
    print()
    
    # Check for quality elements
    quality_elements = [
        "simple black and white line drawing" in content_prompt,
        "thick black outlines only" in content_prompt,
        "no shading" in content_prompt,
        "pure white background" in content_prompt,
        "no text anywhere" in content_prompt
    ]
    
    print("✅ Quality Assurance Checks:")
    quality_labels = [
        "simple line drawing",
        "thick outlines", 
        "no shading",
        "white background",
        "no text"
    ]
    
    for i, check in enumerate(quality_elements):
        status = "✅ PASS" if check else "❌ FAIL"
        print(f"   {status}: {quality_labels[i]}")
    
    print()
    
    # Validate negative prompts
    print("🔍 VALIDATING NEGATIVE PROMPTS:")
    negative_elements = ["text", "words", "letters", "watermark", "complex details"]
    negative_present = [elem in cover_negative for elem in negative_elements]
    
    print("Negative Prompt Coverage:")
    for i, present in enumerate(negative_present):
        status = "✅ PASS" if present else "❌ FAIL"
        print(f"   {status}: blocks '{negative_elements[i]}'")
    
    print()
    
    # Overall assessment
    all_text_checks = all(text_prevention)
    all_quality_checks = all(quality_elements)
    all_negative_checks = all(negative_present)
    
    print("📊 OVERALL ASSESSMENT:")
    print(f"   Text Prevention: {'✅ EXCELLENT' if all_text_checks else '⚠️ NEEDS WORK'}")
    print(f"   Prompt Quality: {'✅ EXCELLENT' if all_quality_checks else '⚠️ NEEDS WORK'}")  
    print(f"   Negative Prompts: {'✅ EXCELLENT' if all_negative_checks else '⚠️ NEEDS WORK'}")
    
    overall_score = sum([all_text_checks, all_quality_checks, all_negative_checks]) / 3 * 100
    print(f"   Overall Score: {overall_score:.0f}%")
    
    if overall_score >= 90:
        print("\n🎉 SYSTEM FIXES SUCCESSFUL!")
        print("✅ Ready for production use")
    elif overall_score >= 70:
        print("\n✅ SYSTEM MUCH IMPROVED")
        print("⚠️ Minor tweaks may be needed")
    else:
        print("\n❌ SYSTEM NEEDS MORE WORK")
        print("🔧 Additional fixes required")
    
    return book

if __name__ == "__main__":
    test_book = test_enhanced_system()