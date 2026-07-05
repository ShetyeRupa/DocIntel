"""Deployment script for Hugging Face Spaces."""
import os
import subprocess
import sys

def deploy_to_huggingface():
    """Deploy DocIntel to Hugging Face Spaces."""
    
    print("🚀 Deploying DocIntel to Hugging Face Spaces")
    print("="*60)
    
    # Check for HF token
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN environment variable not set")
        print("   Get your token from: https://huggingface.co/settings/tokens")
        sys.exit(1)
    
    # Check for space name
    space_name = os.getenv("HF_SPACE_NAME")
    if not space_name:
        space_name = input("Enter your Hugging Face Space name (e.g., username/docintel): ")
    
    print(f"📦 Building Docker image...")
    
    # Build Docker image
    try:
        subprocess.run(
            ["docker", "build", "-t", "docintel", "."],
            check=True,
            capture_output=True
        )
        print("✅ Docker image built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e}")
        sys.exit(1)
    
    # Tag for Hugging Face
    hf_image = f"registry.hf.space/{space_name}:latest"
    print(f"🏷️ Tagging image: {hf_image}")
    
    try:
        subprocess.run(
            ["docker", "tag", "docintel", hf_image],
            check=True
        )
        print("✅ Image tagged successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tagging failed: {e}")
        sys.exit(1)
    
    # Login to Hugging Face
    print("🔑 Logging into Hugging Face...")
    
    try:
        subprocess.run(
            ["docker", "login", "registry.hf.space", "-u", "your-username", "-p", hf_token],
            check=True
        )
        print("✅ Login successful")
    except subprocess.CalledProcessError as e:
        print(f"❌ Login failed: {e}")
        sys.exit(1)
    
    # Push to Hugging Face
    print("📤 Pushing to Hugging Face...")
    
    try:
        subprocess.run(
            ["docker", "push", hf_image],
            check=True
        )
        print("✅ Push successful")
    except subprocess.CalledProcessError as e:
        print(f"❌ Push failed: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Deployment complete!")
    print(f"🌐 Your space is at: https://huggingface.co/spaces/{space_name}")
    print("\n📝 Next steps:")
    print("1. Add GROQ_API_KEY as a secret in your space settings")
    print("2. Wait for the space to build and deploy")
    print("3. Start using DocIntel!")

def create_hf_space():
    """Create a new Hugging Face Space."""
    
    print("📝 Creating Hugging Face Space...")
    
    space_name = input("Enter your desired space name: ")
    username = input("Enter your Hugging Face username: ")
    
    # Create space using HF CLI
    try:
        subprocess.run(
            [
                "huggingface-cli", "repo", "create",
                f"--type", "space",
                f"--space_sdk", "docker",
                f"{username}/{space_name}"
            ],
            check=True
        )
        print(f"✅ Space created: https://huggingface.co/spaces/{username}/{space_name}")
        return f"{username}/{space_name}"
    except subprocess.CalledProcessError as e:
        print(f"❌ Space creation failed: {e}")
        print("\nPlease create your space manually at:")
        print("https://huggingface.co/new-space")
        print("Choose: Docker SDK")
        return None

if __name__ == "__main__":
    print("DocIntel Hugging Face Deployment Tool")
    print("1. Deploy to existing Space")
    print("2. Create new Space and deploy")
    
    choice = input("Select option (1 or 2): ")
    
    if choice == "1":
        deploy_to_huggingface()
    elif choice == "2":
        space_name = create_hf_space()
        if space_name:
            # Set env var and deploy
            os.environ["HF_SPACE_NAME"] = space_name
            deploy_to_huggingface()
    else:
        print("Invalid choice")