"""
Create a sample PDF for testing the Novel AI application
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def create_sample_novel():
    filename = "sample_novel.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>The Magical Forest Adventure</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.5*inch))
    
    # Chapter 1
    ch1_title = Paragraph("<b>Chapter 1: The Discovery</b>", styles['Heading1'])
    story.append(ch1_title)
    story.append(Spacer(1, 0.2*inch))
    
    ch1_text = """
    Once upon a time, in a small village nestled between rolling hills, there lived a curious young girl named Emma. 
    She loved exploring the woods near her home, always searching for new adventures. One sunny morning, while 
    wandering deeper into the forest than ever before, Emma stumbled upon a peculiar tree with shimmering golden leaves.
    
    As she approached the tree, she noticed a small door carved into its trunk. The door was no bigger than her hand, 
    and it glowed with a soft, warm light. Emma's heart raced with excitement. She had heard stories of magical 
    creatures living in the forest, but she never believed they were true. Now, standing before this mysterious door, 
    she couldn't help but wonder what secrets lay beyond it.
    """
    story.append(Paragraph(ch1_text, styles['BodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Chapter 2
    ch2_title = Paragraph("<b>Chapter 2: The Friendly Fairy</b>", styles['Heading1'])
    story.append(ch2_title)
    story.append(Spacer(1, 0.2*inch))
    
    ch2_text = """
    Emma gently knocked on the tiny door. To her amazement, it swung open, and out flew a beautiful fairy with 
    sparkling wings that shimmered like diamonds in the sunlight. The fairy was no taller than Emma's thumb and 
    wore a dress made of flower petals.
    
    "Hello, dear child," the fairy said in a voice as sweet as honey. "My name is Luna. I've been waiting for 
    someone kind and brave like you to find our magical home." Emma could hardly believe her eyes. She had so 
    many questions! Luna smiled warmly and invited Emma to sit beneath the golden tree, promising to share the 
    secrets of the enchanted forest.
    """
    story.append(Paragraph(ch2_text, styles['BodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Chapter 3
    ch3_title = Paragraph("<b>Chapter 3: The Hidden Kingdom</b>", styles['Heading1'])
    story.append(ch3_title)
    story.append(Spacer(1, 0.2*inch))
    
    ch3_text = """
    Luna explained that the golden tree was a gateway to a hidden kingdom where magical creatures lived in harmony. 
    There were talking animals, friendly dragons, and even unicorns that could fly! But the kingdom was in trouble. 
    A dark shadow had been spreading across the land, making the flowers wilt and the streams run dry.
    
    "We need someone from the human world to help us," Luna said, her eyes filled with hope. "Only a pure heart 
    can break the spell that's causing this darkness." Emma felt a surge of courage. She knew she had to help her 
    new friends. Without hesitation, she agreed to embark on this magical quest to save the enchanted kingdom.
    """
    story.append(Paragraph(ch3_text, styles['BodyText']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Sample novel created: {filename}")
    print(f"📚 You can now upload this PDF to test the application!")

if __name__ == "__main__":
    try:
        create_sample_novel()
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "reportlab"])
        create_sample_novel()
