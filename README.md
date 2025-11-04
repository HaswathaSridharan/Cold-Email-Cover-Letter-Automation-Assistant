# ✉️ Cold Email & Cover Letter Automation Assistant

Applying to jobs or reaching out to potential clients typically requires crafting personalized emails and cover letters each time — and that can be exhausting, repetitive, and prone to mistakes.

This project introduces an automated assistant that streamlines the process. It takes your resume and a job posting, understands the role, identifies key requirements, locates the recruiter’s email if needed, and generates:

- ✅ A tailored cold outreach email  
- ✅ A customized cover letter  
- ✅ A ready-to-send professional email with attachments via Gmail  

By automating these repetitive communication tasks, the system helps users save time, maintain consistent professionalism, and significantly increase their chances of receiving a response — both in individual job-seeking scenarios and in business outreach contexts.

---

## 📌 System Overview

This solution combines intelligent text processing, recruiter contact enrichment, and automated email dispatch to support efficient, high-quality outreach.

The system:

- Reads and interprets job descriptions  
- Extracts required skills, role details, and company context  
- Understands user resume content to personalize messaging  
- Finds recruiter emails through lookup if not provided  
- Creates a personalized cover letter   
- Generates a professional cold email aligned with the job or client context  
- Sends emails and attachments securely through Gmail (after user approval)  

### Supported Modes

| Mode | Purpose |
|------|--------|
**Individual Mode** | Tailored job applications with resume + cover letter delivery  
**Organization Mode** | Personalized business outreach and consulting proposals  

---

## 🧠 Technology Application

| System Function | Technology Used |
|-----------------|----------------|
Job parsing & understanding | Groq LLaMA-3 + LangChain prompts  
Resume interpretation | LLM-based semantic parsing  
Recruiter email discovery | Hunter.io API  
Portfolio-to-job match | ChromaDB embeddings + semantic search  
Email & cover letter generation | LLaMA-3 (low-temperature, structured prompts)  
Document creation | Automated DOCX generation pipeline  
Email sending | Gmail API (OAuth secured)  

This architecture blends AI-powered reasoning, API-driven data enrichment, and secure communication workflows to create highly personalized outreach with minimal manual effort.

---

## ✅ Conclusion

This assistant streamlines the outreach process, transforming it from repetitive and time-consuming to efficient and intelligent. It ensures:

- ✔️ Consistent, professional communication  
- ✔️ Reduced manual workload and faster application cycles  
- ✔️ Higher personalization based on job and applicant context  
- ✔️ Improved engagement rates with recruiters and clients  

Ultimately, it allows users to focus on interview preparation, strategy, and opportunity exploration — while the system handles formatting, language, and delivery.

---

## ⭐ Like This Project?

If you find this useful, feel free to ⭐ the repo and share feedback or ideas for improvements!
