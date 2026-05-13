# ===================================================================================
# FILE 4: src/main.py
# ===================================================================================

import sys
import os

def main():
    """Main execution function"""
    
    # Check arguments
    if len(sys.argv) < 3:
        print("\n" + "="*60)
        print("LAPIN TRUST INDEX REPORT GENERATOR")
        print("="*60)
        print("\nUsage: python src/main.py <input_file.xlsx> <output_file.pptx>")
        print("\nExample:")
        print("  python src/main.py data/survey_data.xlsx output/trust_index_report.pptx")
        print("\n" + "="*60)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Check input file exists
    if not os.path.exists(input_file):
        print(f"\n❌ ERROR: Input file '{input_file}' not found!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Looking for: {os.path.abspath(input_file)}")
        sys.exit(1)
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Created output directory: {output_dir}")
    
    print("\n" + "="*60)
    print("LAPIN TRUST INDEX REPORT GENERATOR")
    print("="*60)
    print(f"\nInput:  {input_file}")
    print(f"Output: {output_file}")
    
    try:
        # Import modules (assumes they're in same directory or PYTHONPATH)
        from data_processor import SurveyDataProcessor
        from chart_generator import ChartGenerator
        from presentation_builder import PresentationBuilder
        
        # Step 1: Process data
        print("\n[STEP 1/3] Processing survey data...")
        processor = SurveyDataProcessor(input_file)
        
        # Step 2: Initialize chart generator
        print("\n[STEP 2/3] Initializing chart generator...")
        chart_gen = ChartGenerator(processor)
        print("✓ Chart generator ready")
        
        # Step 3: Build presentation
        print("\n[STEP 3/3] Building PowerPoint presentation...")
        builder = PresentationBuilder(processor, chart_gen)
        prs = builder.build_full_report()
        
        # Save
        print(f"\n💾 Saving presentation to: {output_file}")
        prs.save(output_file)
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Report generated successfully.")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Total slides: {len(prs.slides)}")
        print(f"   • Roles analyzed: {', '.join(processor.roles)}")
        print(f"   • Categories: {', '.join(processor.get_all_categories())}")
        print(f"   • Output file: {os.path.abspath(output_file)}")
        print("\n" + "="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR OCCURRED")
        print("="*60)
        print(f"\nError details: {str(e)}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()