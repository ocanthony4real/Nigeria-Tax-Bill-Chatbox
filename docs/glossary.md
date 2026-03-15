# Glossary

Key terms and definitions related to Nigerian tax law and this project.

---

## Tax Terms

### A

**Assessment**
:   The process by which the tax authority determines the amount of tax owed by a taxpayer based on their income, assets, or transactions.

**Assessable Income**
:   Total income of a taxpayer that is subject to taxation after allowable deductions.

### C

**Capital Gains Tax (CGT)**
:   A tax levied on the profit realized from the sale of a non-inventory asset, such as property or investments.

**Companies Income Tax (CIT)**
:   Tax imposed on the profits of companies operating in Nigeria. Rates vary from 0-30% based on company size.

**Compliance**
:   Adherence to tax laws, including timely filing of returns and payment of taxes.

### D

**Deductible Expenses**
:   Business expenses that can be subtracted from gross income to reduce taxable income, such as operating costs, salaries, and depreciation.

**Double Taxation Agreement (DTA)**
:   A treaty between two countries to prevent the same income from being taxed twice. Nigeria has DTAs with several countries.

### E

**Education Tax**
:   A 2% tax on assessable profits of companies, used to fund the Tertiary Education Trust Fund (TETFund).

**Exempt Income**
:   Income that is not subject to taxation, as specified in the Tax Act (e.g., certain agricultural income).

### F

**FIRS (Federal Inland Revenue Service)**
:   The federal agency responsible for assessing, collecting, and accounting for tax revenue in Nigeria.

**Filing**
:   The act of submitting tax returns and related documents to the tax authority.

### G

**Gross Income**
:   Total income before any deductions or exemptions are applied.

### I

**Income Tax**
:   Tax levied on the income of individuals and entities. In Nigeria, this includes Personal Income Tax and Companies Income Tax.

### M

**Minimum Tax**
:   The minimum amount of tax payable by a company regardless of whether it makes a profit. Typically 0.5% of gross turnover.

### N

**NASENI Tax**
:   A 0.25% levy on profits of companies with turnover above ₦100 million, used to fund the National Agency for Science and Engineering Infrastructure.

**Non-Resident**
:   A person or entity that does not have tax residence in Nigeria but may still be subject to Nigerian tax on income sourced from Nigeria.

### P

**PAYE (Pay As You Earn)**
:   A system where employers deduct income tax from employees' salaries and remit directly to the tax authority.

**Penalty**
:   A financial punishment for non-compliance with tax laws, such as late filing or underpayment.

**Personal Income Tax (PIT)**
:   Tax on the income of individuals, with rates ranging from 7% to 24% based on income brackets.

### R

**Resident**
:   A person or entity that has tax residence in Nigeria and is subject to Nigerian tax on worldwide income.

**Return**
:   A formal document filed with the tax authority declaring income, deductions, and tax liability.

### S

**Self-Assessment**
:   A system where taxpayers calculate their own tax liability and file returns accordingly.

**Stamp Duty**
:   A tax on legal documents and instruments, such as agreements, contracts, and receipts.

### T

**Tax Clearance Certificate (TCC)**
:   A document issued by FIRS confirming that a taxpayer has paid all outstanding taxes. Required for various business activities.

**Tax Identification Number (TIN)**
:   A unique number assigned to taxpayers for identification purposes.

**Taxable Income**
:   Income that is subject to taxation after all allowable deductions and exemptions.

**Transfer Pricing**
:   Rules governing the pricing of transactions between related parties to prevent profit shifting.

### V

**Value Added Tax (VAT)**
:   A consumption tax of 7.5% on goods and services at each stage of production or distribution.

### W

**Withholding Tax (WHT)**
:   Tax deducted at source from payments such as contracts, dividends, and professional fees.

---

## Technical Terms

### E

**Embedding**
:   The process of converting text into numerical vectors that capture semantic meaning. Used in the RAG pipeline to match queries with relevant document chunks.

### F

**Fine-tuning**
:   The process of further training a pre-trained model on domain-specific data to improve performance on specific tasks.

### H

**Hallucination**
:   When an AI model generates false or unsupported information. Our system minimizes this through RAG.

### L

**LLM (Large Language Model)**
:   An AI model trained on vast amounts of text data that can understand and generate human-like text. Example: LLaMA 3.1.

**LoRA (Low-Rank Adaptation)**
:   A parameter-efficient fine-tuning technique that trains only a small number of additional parameters while keeping the base model frozen.

### R

**RAG (Retrieval-Augmented Generation)**
:   A technique that combines information retrieval with text generation, allowing the model to generate responses based on retrieved documents rather than just its training data.

**Reranking**
:   A second-stage ranking process using a cross-encoder model to improve the relevance of retrieved results.

### S

**Semantic Search**
:   A search technique that understands the meaning of queries rather than just matching keywords. Used to find relevant document chunks.

**SFT (Supervised Fine-Tuning)**
:   Training a model on labeled examples to perform a specific task, such as question answering with citations.

### V

**Vector Database**
:   A database optimized for storing and querying high-dimensional vectors. Qdrant is used in this project.

**Vector Search**
:   Finding similar items by comparing their vector representations. Used to retrieve relevant document chunks.

---

## Abbreviations

| Abbreviation | Full Form |
|--------------|-----------|
| API | Application Programming Interface |
| CGT | Capital Gains Tax |
| CI/CD | Continuous Integration/Continuous Deployment |
| CIT | Companies Income Tax |
| DTA | Double Taxation Agreement |
| ECR | Elastic Container Registry |
| FIRS | Federal Inland Revenue Service |
| GPU | Graphics Processing Unit |
| HF | HuggingFace |
| IAM | Identity and Access Management |
| LLM | Large Language Model |
| LoRA | Low-Rank Adaptation |
| PAYE | Pay As You Earn |
| PIT | Personal Income Tax |
| RAG | Retrieval-Augmented Generation |
| SFT | Supervised Fine-Tuning |
| TCC | Tax Clearance Certificate |
| TIN | Tax Identification Number |
| VAT | Value Added Tax |
| WHT | Withholding Tax |

---

## Nigerian Currency

**Naira (₦)**
:   The official currency of Nigeria. Currency code: NGN.

Common denominations referenced in tax law:

| Amount | Common Usage |
|--------|--------------|
| ₦25 million | Small company threshold |
| ₦100 million | Large company threshold |
| ₦500,000 | Various exemption thresholds |

---

## Legal References

**Section**
:   A numbered division of the Tax Act containing specific provisions.

**Part**
:   A major division of the Tax Act containing related sections.

**Chapter**
:   The highest-level division of the Tax Act (e.g., "Companies Income Tax").

**Schedule**
:   Appendices to the Tax Act containing detailed provisions, rates, or lists.

---

## See Also

- [FAQ](faq.md) - Common questions
- [Use Cases](use-cases.md) - Real-world examples
- [API Reference](api/rest-api.md) - Technical documentation
