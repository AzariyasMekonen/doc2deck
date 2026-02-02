import os
from typing import List
import re
import requests

class AIService:
    def __init__(self):
        print("AI Service initialized with OpenRouter Trinity model + enhanced fallback")
        self.use_ai = True
    
    async def generate_notes(self, text: str) -> str:
        """Generate structured notes using OpenRouter Trinity model with fallback"""
        # Try OpenRouter first
        try:
            ai_notes = await self._openrouter_notes(text)
            if ai_notes:
                return ai_notes
        except Exception as e:
            print(f"OpenRouter failed: {e}")
        
        # Fallback to enhanced processing
        return self._enhanced_notes(text)
    
    async def review_presentation(self, notes: str) -> List[str]:
        """Review presentation using OpenRouter with fallback"""
        # Try OpenRouter first
        try:
            ai_feedback = await self._openrouter_feedback(notes)
            if ai_feedback:
                return ai_feedback
        except Exception as e:
            print(f"OpenRouter feedback failed: {e}")
        
        # Fallback to enhanced feedback
        return self._enhanced_feedback(notes)
    
    async def _openrouter_notes(self, text: str) -> str:
        """Generate notes using OpenRouter Trinity model"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return None
            
        import re
        clean_text = re.sub(r'--- Page \d+ ---', '', text)
        clean_text = re.sub(r'\n+', '\n', clean_text).strip()
        
        prompt = f"""Create comprehensive study notes from this content. Follow these rules:

1. Write complete sentences and paragraphs - no incomplete thoughts
2. Use proper headings from the document (## for main topics)
3. Never use bullet points as headings or titles
4. Write in flowing paragraph format with complete explanations
5. Include all important information - don't skip content
6. Use original document structure and headings
7. Don't mention page numbers

Content:
{clean_text}

Create well-structured study notes with proper headings and full paragraphs."""
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "arcee-ai/trinity-large-preview:free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"OpenRouter error: {response.status_code}")
            return None
    
    async def _openrouter_feedback(self, notes: str) -> List[str]:
        """Get feedback using OpenRouter Trinity model"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return None
            
        prompt = f"""Review this presentation content and give 3-5 specific feedback points:

{notes}

Focus on: slide length, clarity, structure, best practices."""
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "arcee-ai/trinity-large-preview:free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            feedback_text = result['choices'][0]['message']['content']
            feedback = feedback_text.split('\n')
            return [f.strip() for f in feedback if f.strip()][:10]
        else:
            return None
    
    def _enhanced_notes(self, text: str) -> str:
        """Enhanced notes generation with better structure"""
        import re
        
        # Clean text and remove page markers
        clean_text = re.sub(r'--- Page \d+ ---', '', text)
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        
        notes = "# Study Notes\n\n"
        current_section = ""
        current_content = []
        
        for line in lines:
            # Detect headings (capitalized, not too long, not ending with period)
            if (len(line) > 3 and len(line) < 80 and 
                not line.endswith('.') and 
                not line.startswith(('•', '-', '*', '1.', '2.', '3.')) and
                (line[0].isupper() or line.startswith('Chapter') or line.startswith('Section'))):
                
                # Save previous section
                if current_section and current_content:
                    notes += f"## {current_section}\n\n"
                    # Create flowing paragraphs
                    paragraph = self._create_paragraph(current_content)
                    notes += f"{paragraph}\n\n"
                
                current_section = line
                current_content = []
                
            # Add content (skip bullet markers)
            elif len(line) > 10:
                clean_line = re.sub(r'^[•\-\*]\s*', '', line)
                current_content.append(clean_line)
        
        # Add final section
        if current_section and current_content:
            notes += f"## {current_section}\n\n"
            paragraph = self._create_paragraph(current_content)
            notes += f"{paragraph}\n\n"
        
        return notes
    
    def _create_paragraph(self, content_list: List[str]) -> str:
        """Create flowing paragraphs from content list"""
        if not content_list:
            return ""
        
        # Join sentences intelligently
        text = " ".join(content_list)
        
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Create paragraphs (max 4-5 sentences each)
        paragraphs = []
        current_para = []
        
        for sentence in sentences:
            current_para.append(sentence)
            if len(current_para) >= 4:
                paragraphs.append(". ".join(current_para) + ".")
                current_para = []
        
        # Add remaining sentences
        if current_para:
            paragraphs.append(". ".join(current_para) + ".")
        
        return "\n\n".join(paragraphs)
    
    def _enhanced_feedback(self, notes: str) -> List[str]:
        """Enhanced feedback based on content analysis"""
        feedback = []
        
        # Analyze content length
        sections = notes.split('##')
        if len(sections) > 8:
            feedback.append("Consider combining related sections to reduce the number of slides")
        
        # Check for very long paragraphs
        long_paragraphs = [s for s in sections if len(s) > 500]
        if long_paragraphs:
            feedback.append("Some sections are too long - break them into multiple slides")
        
        # Check for very short sections
        short_sections = [s for s in sections if len(s.strip()) < 50 and s.strip()]
        if short_sections:
            feedback.append("Some sections are too brief - consider adding more detail or combining with other sections")
        
        # General recommendations
        feedback.extend([
            "Ensure each slide has a clear, descriptive title",
            "Use consistent formatting throughout the presentation",
            "Consider adding examples or illustrations where appropriate"
        ])
        
        return feedback[:10]
    
    def _fallback_feedback(self) -> List[str]:
        """Fallback feedback when AI is not available"""
        return [
            "Consider breaking long slides into multiple slides",
            "Ensure each slide has a clear, descriptive title",
            "Use bullet points instead of long paragraphs",
            "Keep text concise and readable",
            "Review slide flow and logical progression"
        ]