# ================== chains.py ==================
import os
import re
import json
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

load_dotenv()

# ----------------- ORGANIZATION PATH (CONSULTING MANAGER) -----------------
class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the
            following keys: role, experience, skills, description, company name, recruiter_name.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Haswatha Sridharan, a Business Development Executive at InnovaEdge Technologies.
            Craft a cold outreach email highlighting how InnovaEdge’s experience and portfolio can help the client.
            Include the following portfolio links:
            {link_list}

            Tone: Professional, confident, outcome-driven.

            End the email with:
            Warm Regards,  
            Haswatha Sridharan  
            Business Development Executive, InnovaEdge Technologies
            Phone: 777-444-0000 

            Output ONLY the email body (no explanations).
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content.strip()

# ----------------- INDIVIDUAL PATH (STUDENT PATH) -----------------
class IndividualChain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-70b-8192"
        )
        self.client = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-8b-8192"
        )
        self.hunter_api_key = os.getenv("HUNTER_API_KEY")

    def extract_job_info(self, cleaned_text):
        prompt = f"""
        ### SCRAPED TEXT FROM WEBSITE:
        {cleaned_text}
        ### INSTRUCTION:
        Extract job details in valid JSON with the following snake_case keys:
        - role
        - experience
        - skills
        - description
        - company_name
        - recruiter_name
        - recruiter_email

        Return ONLY valid JSON. No preambles, no markdown.
        """
        result = self.llm.invoke(prompt.strip())
        content = result.content.strip()

        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            raise ValueError(f"Failed to find JSON in LLM response.\nContent was: {content}")

        json_text = json_match.group(0)

        try:
            job = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse extracted JSON: {e}\nContent was: {json_text}")

        return job

    def extract_contact_info(self, text):
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        phone_match = re.search(r"(\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        linkedin_match = re.search(r"(https?://)?(www\.)?(linkedin\.com/in/[a-zA-Z0-9-_/]+)", text)

        return {
            "email": email_match.group(0) if email_match else "youremail@example.com",
            "phone": phone_match.group(0) if phone_match else "(123) 456-7890",
            "linkedin": linkedin_match.group(0) if linkedin_match else "https://linkedin.com/in/yourname",
            "name": "Your Name"
        }

    def lookup_recruiter_email(self, recruiter_name, company_name):
        try:
            domain_resp = requests.get(
                f"https://api.hunter.io/v2/domain-search?company={company_name}&api_key={self.hunter_api_key}"
            ).json()
            domain = domain_resp.get("data", {}).get("domain", "")
            if not domain:
                return ""
            email_resp = requests.get(
                "https://api.hunter.io/v2/email-finder",
                params={"full_name": recruiter_name, "domain": domain, "api_key": self.hunter_api_key}
            ).json()
            return email_resp.get("data", {}).get("email", "")
        except Exception as e:
            print(f"Error in recruiter email lookup: {e}")
            return ""

    def generate_cover_letter(self, job, resume_text):
        prompt = f"""
        You are helping write a professional cover letter.

        Write a confident cover letter for:
        - Role: {job.get('role')}
        - Company: {job.get('company_name')}
        - Description: {job.get('description')}

        Resume:
        -------------------------------
        {resume_text}
        -------------------------------

        ### INSTRUCTIONS (STRICT):
        - Start the cover letter with the applicant’s full name
        - Do **not** include any heading like "Generated Cover Letter" or "Cover Letter:"
        - Do **not** include preambles, explanations, or markdown
        - The letter must be formal, focused, and personalized
        - Do **NOT** use placeholder text like "[Your Name]" or "[Current Date]"
        - Only output the final formatted cover letter body starting with the applicant's name

        Output ONLY the cover letter body. No text heading, No Preambles.
        ### COVER LETTER BODY (NO PREAMBLE, NO HEADING):
        """
        result = self.client.invoke(prompt.strip())
        return result.content.strip()

    def generate_cold_email(self, job, applicant_info, cover_letter_text):
        # Improved logic to extract the first non-empty line as name
        lines = cover_letter_text.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines

        # Now pick the first meaningful line
        if lines:
            first_line = lines[0]
            # Optional: only if first line is likely a name (heuristic: 2-4 words, all alphabetic)
            if 2 <= len(first_line.split()) <= 4 and all(word.isalpha() for word in first_line.split()):
                applicant_info["name"] = first_line


        recruiter = job.get("recruiter_name", "").split()[0] if job.get("recruiter_name") else None
        greeting = f"Hello {recruiter}," if recruiter else "To Whom It May Concern,"

        prompt = f"""
### JOB DESCRIPTION:
{json.dumps(job, indent=2)}

### INSTRUCTION:
You are writing a cold outreach email for the {job.get('role')} role at {job.get('company_name')}.

- Start with "{greeting}"
- Maintain a professional and warm tone
- End with:

Best Regards,
[Your Name]
[Phone] | [Email]

Only output the email, no explanations, no markdown formatting.
Do not provide a preamble.
### EMAIL (NO PREAMBLE):
        """

        result = self.client.invoke(prompt.strip())
        # After LLM generates the raw email
        final_email = result.content.strip()

        # Clean any hallucinated cover letters
        keywords = ["here is the cover letter", "attached is the cover letter", "generated cover letter"]
        lines = final_email.splitlines()
        lines = [line for line in lines if not any(k in line.lower() for k in keywords)]
        final_email = "\n".join(lines).strip()

        # Forcefully replace or insert correct signature
        signature_text = f"""
        Best Regards,
        {applicant_info.get("name", "Your Name")}
        {applicant_info.get("phone", "(123) 456-7890")} | {applicant_info.get("email", "youremail@example.com")}
        """.strip()

        # If "Best Regards," is already in the text, truncate from there and replace
        if "Best Regards," in final_email:
            final_email = final_email.split("Best Regards,")[0].strip()

        # Now add clean signature
        final_email = final_email + "\n\n" + signature_text
        return final_email