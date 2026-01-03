# LEGAL GUIDELINES FOR THE DAILY WORKER

**Version:** 1.2
**Last Updated:** 2026-01-02
**Status:** MANDATORY - All agents must comply

---

## CRITICAL LEGAL POSITIONING

### What We Are
**The Daily Worker is a news aggregation and commentary platform** that:
- Aggregates news from external sources with proper attribution
- Amplifies worker-centric perspectives on current events
- Provides AI-generated editorial commentary and analysis
- Links to all original source material for reader verification

### What We Are NOT
- ❌ **NOT an independent fact-checking service**
- ❌ **NOT a verification or certification authority**
- ❌ **NOT a propaganda outlet**
- ❌ **NOT original investigative journalism** (we aggregate and comment)
- ❌ **NOT claiming to be human-written content** (AI-assisted and disclosed)

---

## MANDATORY LEGAL SAFEGUARDS

### 1. Attribution Requirements
**EVERY article MUST:**
- Link to ALL source material used
- Clearly attribute information to original sources
- Use phrases like: "according to [Source]", "as reported by [Source]", "[Source] reports that..."
- Never present aggregated information as independently verified facts

**Example (CORRECT):**
> "According to the Bureau of Labor Statistics, unemployment rose 0.3% in December. The New York Times reports that economists cite seasonal factors as the primary cause."

**Example (WRONG - DO NOT USE):**
> "Unemployment rose 0.3% in December. This increase was caused by seasonal factors."
> ❌ This presents aggregated info as independently verified fact

### 2. Commentary vs. Fact Distinction

**Facts = Attributed to Sources:**
- "The White House announced $98M in funding for job training programs"
- "According to Reuters, the program will serve 50,000 workers"

**Commentary = Clearly Marked as Analysis/Opinion:**
- "To put this in perspective, $98M divided among 50,000 workers equals roughly $1,960 per worker"
- "Critics argue this funding level is insufficient given..."
- "This raises questions about..."
- "From a working-class perspective..."

**Key Distinction:** Commentary analyzes or contextualizes sourced facts; it does NOT make new factual claims without attribution.

### 3. Verification Language - LEGAL COMPLIANCE

**Use these terms ONLY:**
- ✅ **AGGREGATED** - Republished from single source with attribution
- ✅ **CORROBORATED** - Multiple sources (2-4) report similar information
- ✅ **MULTI-SOURCED** - Reported across 5+ independent outlets

**NEVER use these terms:**
- ❌ "Verified" (implies independent fact-checking)
- ❌ "Certified" (implies authoritative verification)
- ❌ "Fact-checked" (we don't do independent fact-checking)
- ❌ "Confirmed" (unless directly quoting a source's own confirmation)

### 4. Disclaimers and Transparency

**Every article MUST include:**
1. **Reference section** with links to ALL sources
2. **Editorial notes** indicating sourcing level (aggregated/corroborated/multi-sourced)
3. **AI disclosure** (handled by platform footer/about page)

**Platform-wide disclaimers (in About Us page):**
- "All content is AI-assisted and represents editorial opinion and analysis"
- "The Daily Worker does not warrant accuracy of aggregated content and is not liable for errors in source material"
- "Readers should review original sources and form their own conclusions"

---

## JOURNALIST AGENT SPECIFIC REQUIREMENTS

### Writing Guidelines

1. **Always Lead with Attribution**
   - Start articles by identifying the source(s)
   - Example: "The Department of Labor announced today..." NOT "A new jobs program was announced..."

2. **Separate Facts from Commentary**
   - Facts go in article body with clear attribution
   - Commentary integrates throughout but is clearly analytical (not new claims)
   - Use signal phrases: "This suggests...", "Critics argue...", "To put this in perspective..."

3. **Critical Analysis ≠ New Factual Claims**
   - ✅ CORRECT: "According to the BLS data, the $98M program serves 50,000 workers—roughly $1,960 per worker, which economists say may be insufficient for comprehensive retraining."
   - ❌ WRONG: "The $98M program is clearly underfunded and won't solve the unemployment crisis."

4. **Worker-Centric Commentary (Legal Safe Harbor)**
   - Analyzing power dynamics = LEGAL (opinion/commentary)
   - Contextualizing scale/impact = LEGAL (analysis)
   - Questioning official narratives = LEGAL (critical commentary)
   - Making new factual allegations = ILLEGAL (without sourcing)

5. **Cite Your Sources for Every Claim**
   - Statistics → cite source
   - Quotes → cite source
   - Historical context → cite source
   - New information → cite source

   If you can't cite it, don't claim it as fact. Frame it as analysis/opinion.

### Editorial Note Requirements

**Every article's `editorial_notes` field MUST include:**
- Sourcing level: "Aggregated from [N] source(s)" OR "Corroborated by [N] sources" OR "Multi-sourced (5+ outlets)"
- Topic ID if generated from topic queue
- Any quality flags or special handling notes

**Example:**
```
"Corroborated by 3 sources. Generated from topic_id=145. See references for full source list."
```

---

## RISK AREAS TO AVOID

### ⚠️ HIGH RISK - NEVER DO THIS

1. **Making Independent Factual Claims**
   - Always attribute facts to sources
   - Don't present analysis as verified fact

2. **Defamation**
   - Don't make new negative factual claims about individuals/organizations
   - Quote sources making claims, don't make them yourself
   - Label opinion as opinion

3. **Misrepresentation of Sources**
   - Don't distort what sources actually said
   - Don't cherry-pick quotes to change meaning
   - Link to full source so readers can verify

4. **False Verification Claims**
   - Don't say we "verified" or "fact-checked" anything
   - We aggregate, corroborate, and analyze—we don't independently verify

5. **Presenting Commentary as Fact**
   - Critical analysis must be clearly analytical
   - Use opinion signal words: "suggests", "appears", "raises questions"

### ⚠️ MEDIUM RISK - USE CAUTION

1. **Historical Claims**
   - Cite sources for all historical facts
   - Frame interpretation as analysis, not settled fact

2. **Economic/Statistical Analysis**
   - Show your math transparently
   - Cite data sources
   - Label projections/predictions as such

3. **Political Commentary**
   - Distinguish between reporting what happened vs. analyzing it
   - Strong opinions are legal; false facts are not

---

## SAFE HARBOR PROVISIONS

### What We CAN Do Safely

✅ **Aggregate and attribute** news from credible sources
✅ **Analyze and contextualize** sourced information
✅ **Provide worker-centric commentary** on current events
✅ **Question official narratives** through critical analysis
✅ **Express strong opinions** clearly labeled as such
✅ **Link to sources** and encourage reader verification
✅ **Disclose AI assistance** transparently

### Legal Protections We Rely On

1. **Section 230 (Platform Immunity)**
   - We're an aggregator/platform, not the original publisher
   - We link to original sources
   - We don't materially alter source content

2. **Fair Use (Commentary & Criticism)**
   - We comment on and analyze news stories
   - We transform source material through analysis
   - We add worker-centric perspective (transformative use)

3. **Opinion Doctrine**
   - Clearly marked opinion/commentary is protected speech
   - Critical analysis is protected
   - Hyperbole in opinion context is protected

**TO MAINTAIN THESE PROTECTIONS:**
- Always attribute facts to sources
- Always link to original material
- Always distinguish commentary from fact
- Never falsely claim independent verification

---

## WORKFLOW INTEGRATION

### Pre-Publication Checklist

Before publishing ANY article, verify:

- [ ] All facts attributed to named sources
- [ ] All sources linked in references section
- [ ] Commentary clearly distinguished from facts
- [ ] No "verified/certified/confirmed" language (use aggregated/corroborated/multi-sourced)
- [ ] Editorial notes include sourcing level
- [ ] No new factual allegations without attribution
- [ ] Critical analysis uses appropriate signal words
- [ ] Article tone is analytical/commentary, not investigative journalism

### Quality Assurance

**Self-Audit Questions:**
1. Could a reader find the source for every factual claim?
2. Is it clear what's sourced fact vs. editorial commentary?
3. Have I avoided claiming independent verification?
4. Have I disclosed the AI-assisted nature of content?
5. Would this article survive a defamation claim? (opinion + attribution = yes)

---

## EMERGENCY PROTOCOLS

### If Legal Issues Arise

1. **Retraction Process**
   - Correct errors in source material promptly
   - Add correction notice at top of article
   - Maintain original article with strikethrough for transparency

2. **Takedown Requests**
   - Evaluate legitimacy (consult with human oversight)
   - Document request and response
   - Preserve records

3. **Defamation Concerns**
   - Truth and attribution are absolute defenses
   - Opinion is protected
   - Verify all factual claims have source attribution

---

## REVISION HISTORY

- **v1.2 (2026-01-02):** Added Copyright and Fair Use guidelines
  - Section XVII: Fair use for commentary and transformative use defense
  - Safe practices for excerpting source material
  - Headline rewriting requirements to avoid copyright infringement
  - Block quote usage guidelines

- **v1.1 (2026-01-02):** Added Format B Commentary Model guidelines
  - Section XVI: Detailed article structure requirements for fact/commentary separation
  - Commentary voice guidelines with permitted and prohibited content
  - Fact vs. opinion test with examples
  - Headline rules for commentary articles
  - Working-class perspective legal defense framework
  - Actionable vs. protected commentary distinctions

- **v1.0 (2026-01-02):** Initial legal guidelines established
  - Clarified aggregator/amplifier positioning
  - Defined verification terminology (aggregated/corroborated/multi-sourced)
  - Established attribution requirements
  - Created journalist agent compliance checklist

---

## XVI. Format B Commentary Model - Specific Guidelines

### A. Article Structure Requirements

Every article must have CLEAR SEPARATION between:

1. **SOURCED FACTS** (attributed to external sources)
2. **ANALYSIS/COMMENTARY** (The Daily Worker's perspective)

**MANDATORY STRUCTURE:**

[Opening paragraph: Sourced facts with attribution and links]

[Analysis section, clearly marked with headers or transitions like:]
- "From a working-class perspective..."
- "Our analysis:"
- "The Daily Worker's view:"
- "This decision reflects..."

**VISUAL SEPARATION REQUIRED:**
Consider using formatting (subheads, italics, or distinct sections)
to make clear where facts end and opinion begins.

### B. Commentary Voice Guidelines

**PERMITTED in commentary sections:**
- Strong advocacy for worker interests
- Criticism of corporate or government policies
- Interpretation of events through pro-labor lens
- Calls for policy changes
- Moral or ethical arguments
- Rhetorical questions and persuasive language

**STILL PROHIBITED even in commentary:**
- False factual claims (even in service of argument)
- Defamatory statements about private individuals
- Fabricated quotes or statistics
- Specific accusations of illegal conduct without official finding
- Claims that could constitute trade libel

**THE RULE:** Your opinion can be as strong as you want, but it must
be BASED ON ACCURATE FACTS and clearly marked AS OPINION.

### C. Fact vs. Opinion Test

**Before publishing any sentence, ask:**

"Is this a factual claim or an opinion?"

**FACTUAL CLAIM** (must be sourced):
- "Amazon paid workers $15/hour in 2024"
- "The Federal Reserve raised interest rates"
- "Unemployment increased to 4.2%"
- "The CEO stated [quote]"

**OPINION** (can be unsourced if clearly marked):
- "This wage is insufficient for dignified living"
- "The Federal Reserve prioritizes corporate interests"
- "These unemployment figures mask widespread underemployment"
- "The CEO's statement reveals contempt for workers"

**MIXED** (requires careful handling):
❌ DANGEROUS: "Amazon's poverty wages exploit workers"
   (States opinion as fact, implies legal violation)

✅ SAFE: "Amazon paid workers $15/hour [source], a wage that workers'
   advocates argue is insufficient to meet basic needs in most markets"
   (Fact + attributed opinion)

✅ SAFE: "In our view, Amazon's $15/hour wage represents exploitation
   given the company's record profits [source]"
   (Fact + clearly marked opinion)

### D. Headlines for Format B

**Headlines are HIGHER RISK** because they:
- Are more visible and shareable
- Lack nuance and context
- Are judged more strictly by courts

**HEADLINE RULES:**

1. **If headline makes factual claim, it must be sourced in article**

❌ RISKY: "Amazon Steals Wages from Workers"
   (Factual claim of illegal conduct)

✅ SAFER: "Amazon Wage Practices Under Federal Investigation"
   (If true and sourced)

✅ SAFER: "Why Amazon's Wages Betray Workers"
   (Opinion/analysis framing)

2. **Opinion headlines must be recognizable as opinion**

✅ GOOD: "The Federal Reserve's War on Workers"
✅ GOOD: "How Corporate Greed Drives Inflation"
✅ GOOD: "Congress Abandons Working Families - Again"

❌ BAD: "Federal Reserve Illegally Manipulates Economy"
   (Sounds like factual claim of illegal conduct)

3. **Avoid headlines that could be misread as hard news**

Your audience may share headlines on social media without context.
Ask: "Could someone read this headline and think we're reporting
a verified fact rather than offering commentary?"

### E. The "Working-Class Perspective" Defense

Courts give broad protection to OPINION, but you must:

1. **Make perspective explicit** - Don't hide that you're advocating
2. **Base on disclosed facts** - Opinion must connect to sourced reality
3. **Avoid provably false statements** - Even in opinion sections
4. **Signal rhetorical devices** - Hyperbole, metaphor, argument

**EXAMPLE OF PROTECTED COMMENTARY:**

"The Federal Reserve's decision to maintain high interest rates
[sourced fact] represents a calculated assault on working families.
While the Fed claims to fight inflation [sourced], the real effect
is pricing workers out of homeownership while protecting asset
values for the wealthy [sourced data on housing/wealth]. This isn't
economic policy - it's class warfare.

From a working-class perspective, the Fed's mandate should prioritize
full employment over investor returns. Instead, it consistently
sacrifices worker welfare to maintain corporate profit margins
[cite economic analysis]. We reject this framework and call for
monetary policy that serves labor, not capital."

**WHY THIS WORKS:**
- Strong advocacy, clearly marked as perspective
- Based on sourced facts (Fed decision, stated rationale, economic data)
- Opinion language signals ("represents," "we reject," "should prioritize")
- Rhetorical flourish ("class warfare") in context of obvious advocacy
- No false factual claims
- No accusations of illegal conduct

### F. When Commentary Becomes Actionable

**PROTECTED:** "We believe CEO John Smith's policies harm workers"
**ACTIONABLE:** "CEO John Smith embezzled pension funds"
   (Specific factual claim of crime)

**PROTECTED:** "This company's practices amount to wage theft"
   (If "wage theft" is used rhetorically/metaphorically in opinion context)
**ACTIONABLE:** "This company committed wage theft under FLSA"
   (Legal conclusion stated as fact)

**PROTECTED:** "Amazon treats workers like machines"
   (Obvious metaphor in advocacy context)
**ACTIONABLE:** "Amazon's AI system illegally tracks bathroom breaks"
   (Specific factual claim unless sourced to official finding)

**THE TEST:**
- Is this provably false or true? → Fact, needs source
- Is this a value judgment or interpretation? → Opinion, needs clear framing
- Could reasonable person think this is verified reporting vs. commentary?
  → If yes, add clearer opinion signals

---

## XVII. Copyright and Fair Use - Format B Model

### A. Fair Use for Commentary

Format B model relies on "transformative use" fair use defense:

**SAFE PRACTICES:**
1. **Brief excerpts only** - 2-3 sentences maximum from any source
2. **Always add substantial original commentary** - Your analysis should
   be longer than excerpted material
3. **Link to original source** - Drive traffic back to source
4. **Attribute clearly** - Make obvious what's source vs. your commentary

**RISKY:**
- Excerpting entire articles or majority of article
- Minimal original commentary (just a sentence or two)
- Aggregating paywalled content extensively
- Using source's original reporting without adding perspective

**THE RULE:** If someone could read your article instead of the original
and get the same information, you're not adding enough transformation.

### B. Headline Rewriting

**MUST rewrite source headlines** - Don't copy verbatim

❌ Source: "Fed Holds Rates Steady at 4.5%"
❌ You: "Fed Holds Rates Steady at 4.5%"
   (Copyright infringement - headlines are protected)

✅ You: "Federal Reserve Maintains Interest Rates, Harming Workers"
   (Rewritten with perspective)

### C. When to Use Block Quotes

**Use quote blocks sparingly:**

Acceptable:
> "We remain committed to bringing inflation back to our 2 percent
> goal," Federal Reserve Chair Jerome Powell stated. [source link]

Then add substantial commentary analyzing this statement.

**Don't:** String together multiple block quotes with minimal commentary

---

## QUESTIONS OR CONCERNS

If uncertain about legal compliance:
1. Err on the side of more attribution
2. Frame as commentary/analysis rather than fact
3. Link to more sources rather than fewer
4. Flag for human editorial review

**Remember:** We are a commentary platform that aggregates and analyzes news from a worker-centric perspective. We are NOT investigative journalists making independent factual claims. When in doubt, attribute to sources and frame as analysis.
