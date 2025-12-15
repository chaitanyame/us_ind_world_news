# TOON Format Research for NRI News Brief Platform

**Research Date:** December 15, 2025  
**Repository:** [toon-format/toon](https://github.com/toon-format/toon)  
**Purpose:** Evaluate TOON format viability for token-optimized news bulletin storage

---

## 1. Toon Format Overview

### What is TOON?

**TOON (Token-Oriented Object Notation)** is a compact, human-readable data encoding format that represents the JSON data model with significantly reduced token usage. It's designed specifically for Large Language Model (LLM) contexts where token efficiency directly impacts costs and performance.

### How It Works

TOON combines two core strategies:
- **YAML-like indentation**: Uses indentation instead of braces `{}` for nested objects
- **CSV-style tabular layout**: For uniform arrays of objects, declares field names once and streams row values

### Token Optimization Strategy

TOON achieves token reduction through:

1. **Minimal Punctuation**: Eliminates braces `{}`, brackets `[]`, and most quotation marks
2. **Smart Quoting**: Only quotes strings when necessary for parsing (empty strings, leading/trailing whitespace, reserved words like `true`/`false`/`null`, numbers)
3. **Inline Arrays**: Primitive arrays use comma-separated values instead of individual lines
4. **Tabular Format**: Uniform object arrays declare fields once with a header, then stream data rows
5. **Indentation-Based Structure**: Nested objects use indentation (like YAML) rather than braces

### Example Comparison

**JSON (187 tokens):**
```json
{
  "customers": [
    { "id": 1, "name": "Alice Smith", "email": "alice@example.com", "status": "active", "plan": "premium" },
    { "id": 2, "name": "Bob Johnson", "email": "bob@example.com", "status": "active", "plan": "basic" },
    { "id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "status": "inactive", "plan": "free" }
  ]
}
```

**TOON (72 tokens - 61.5% reduction):**
```
customers[3]{id,name,email,status,plan}:
  1,Alice Smith,alice@example.com,active,premium
  2,Bob Johnson,bob@example.com,active,basic
  3,Charlie Brown,charlie@example.com,inactive,free
```

---

## 2. Encoding/Decoding Specification

### Core Data Model

TOON preserves the JSON data model exactly:
- **Primitives**: string, number, boolean, null
- **Objects**: Key-value mappings (object key order preserved)
- **Arrays**: Ordered sequences (array order preserved)
- **Lossless**: Deterministic round-trip conversion (JSON → TOON → JSON)

### Encoding Rules

**Objects:**
```
key: value              # Simple key-value for primitives
user:                   # Nested object (depth +1 for children)
  name: Alice
  age: 30
```

**Arrays - Primitive (inline):**
```
tags[3]: javascript,python,rust
```

**Arrays - Tabular (uniform objects):**
```
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
```

**Arrays - Expanded (non-uniform/nested objects):**
```
items[2]:
  - id: 1
    name: Item A
  - id: 2
    name: Item B
```

### Delimiter Options

TOON supports three delimiters (declared in array headers):
- **Comma** `,` (default): `key[3]:`
- **Tab** `\t`: `key[3	]:` (often 5-10% more token efficient)
- **Pipe** `|`: `key[3|]:`

### Quoting Rules

Strings must be quoted if they:
- Are empty: `""`
- Have leading/trailing whitespace: `" hello "`
- Equal reserved words: `"true"`, `"false"`, `"null"`
- Look like numbers: `"123"`, `"3.14"`
- Contain special characters: commas, colons, newlines, or the active delimiter

**Valid escapes:** `\\`, `\"`, `\n`, `\r`, `\t` (only these five)

### Number Formatting

**Encoding (canonical form):**
- No exponent notation: `1000000` not `1e6`
- No leading zeros: `5` not `05`
- No trailing zeros: `1.5` not `1.5000`
- Integer form if fractional part is zero: `42` not `42.0`
- Normalize `-0` to `0`

**Decoding (accepted forms):**
- Standard decimals: `42`, `-3.14`
- Exponent forms: `1e-6`, `-1E+9`
- Rejects forbidden leading zeros: `"05"` treated as string

### File Format

- **Extension**: `.toon`
- **Media type**: `text/toon` (provisional)
- **Encoding**: UTF-8 (always)
- **Line endings**: LF (U+000A) - encoders MUST use LF
- **Indentation**: Spaces only (default 2 spaces per level), tabs NOT allowed for indentation

---

## 3. Token Savings Analysis

### Benchmark Results

**Overall Efficiency (Mixed-Structure Track):**

| Format | Tokens | Accuracy | Efficiency Score* |
|--------|--------|----------|------------------|
| TOON | 2,744 | 73.9% | **26.9** |
| JSON (compact) | 3,081 | 70.7% | 22.9 |
| YAML | 3,719 | 69.0% | 18.6 |
| JSON | 4,545 | 69.7% | 15.3 |
| XML | 5,167 | 67.1% | 13.0 |

*Efficiency = (Accuracy % ÷ Tokens) × 1,000

**Key Finding:** TOON achieves **73.9% accuracy** (vs JSON's 69.7%) while using **39.6% fewer tokens** than standard JSON.

### Token Savings by Data Structure

**Flat Tabular Data (100% uniform):**
- **Employee records**: -60.7% vs JSON, -36.8% vs JSON compact
- **Time-series data**: -59.0% vs JSON, -35.8% vs JSON compact
- **GitHub repos**: -42.3% vs JSON, -23.7% vs JSON compact
- **CSV comparison**: TOON uses ~6% more tokens than CSV (acceptable trade-off for added structure)

**Mixed Structure Data:**
- **E-commerce orders** (33% tabular): -33.1% vs JSON
- **Semi-uniform logs** (50% tabular): -15.0% vs JSON
- **Deeply nested config** (0% tabular): -31.3% vs JSON

### File Size Comparison

TOON achieves approximately **30-40% smaller file sizes** compared to JSON:
- Reduced punctuation (braces, brackets, quotes)
- Compact tabular representation
- Minimal whitespace
- No redundant field name repetition in arrays

### When Token Savings Are Maximum

TOON excels with:
1. **Uniform arrays of objects** (same fields across all items): 50-60% savings
2. **Flat tabular data**: 40-60% savings
3. **Mixed structures with some uniform arrays**: 20-40% savings

### When Token Savings Are Minimal

TOON provides minimal benefit for:
1. **Deeply nested structures** (tabular eligibility ~0%): JSON may be more efficient
2. **Semi-uniform arrays** (~40-60% tabular eligibility): Savings diminish
3. **Pure flat tables with no nesting**: CSV is more compact

---

## 4. Browser Compatibility

### Vanilla JavaScript Support

**Yes, TOON format is fully compatible with vanilla JavaScript in browsers.**

#### Official NPM Package

**Package:** `@toon-format/toon`  
**Installation:**
```bash
npm install @toon-format/toon
# or
yarn add @toon-format/toon
# or
pnpm add @toon-format/toon
```

#### Browser Usage (ES6 Modules)

**Modern Browsers (ES6 import):**
```javascript
import { encode, decode } from '@toon-format/toon';

// Encode JSON to TOON
const data = { users: [{ id: 1, name: 'Alice' }] };
const toonString = encode(data);

// Decode TOON to JSON
const jsonData = decode(toonString);
```

**Using a bundler (Webpack, Vite, Rollup):**
The library is designed for modern JavaScript build tools and will bundle seamlessly for browser delivery.

**CDN Usage:**
While the official package is published to npm, it can be loaded via CDN services that auto-publish npm packages:
- unpkg: `https://unpkg.com/@toon-format/toon`
- jsDelivr: `https://cdn.jsdelivr.net/npm/@toon-format/toon`

#### Browser API

**Encoding:**
```javascript
import { encode } from '@toon-format/toon';

const articles = {
  bulletins: [
    { title: "News 1", summary: "Summary 1", category: "US" },
    { title: "News 2", summary: "Summary 2", category: "India" }
  ]
};

const toonOutput = encode(articles, {
  indent: 2,      // spaces per level
  delimiter: ','  // or '\t' or '|'
});
```

**Decoding:**
```javascript
import { decode } from '@toon-format/toon';

const toonString = `
bulletins[2]{title,summary,category}:
  News 1,Summary 1,US
  News 2,Summary 2,India
`;

const data = decode(toonString);
console.log(data.bulletins[0].title); // "News 1"
```

**Streaming (for large datasets):**
```javascript
import { encodeLines, decodeFromLines } from '@toon-format/toon';

// Memory-efficient line-by-line encoding
for (const line of encodeLines(largeData)) {
  // Process each line
}

// Streaming decode
const decoded = decodeFromLines(lineIterator);
```

### Performance Considerations

**Parsing Speed:**
- TOON parsing is reported to be **up to 4.8x faster** than JSON parsing (based on third-party benchmarks)
- Line-oriented format allows for efficient streaming and incremental parsing
- Lower token count means less data transferred over network

**Memory Efficiency:**
- Smaller file sizes reduce memory footprint
- Streaming APIs (encodeLines/decodeFromLines) enable processing large datasets without loading entire structure

**Browser Limitations:**
- No native browser API support (unlike `JSON.parse()`/`JSON.stringify()`)
- Requires bundled library (~23.7 KB for Python implementation, TypeScript likely similar)
- Minimal overhead compared to JSON libraries

### Client-Side Parsing Verdict

✅ **Fully viable for vanilla JavaScript in browsers:**
- Official TypeScript/JavaScript implementation available
- ES6 module support for modern bundlers
- Can be loaded via CDN or bundled into app
- Streaming APIs for large datasets
- Fast parsing performance
- Small library footprint

---

## 5. Available Libraries

### Official Implementations

#### TypeScript/JavaScript (Stable)
- **Package:** `@toon-format/toon`
- **Repository:** [toon-format/toon](https://github.com/toon-format/toon)
- **Status:** ✅ Stable (20.7k stars)
- **Installation:** `npm install @toon-format/toon`
- **Features:**
  - Encode/decode with options (indent, delimiter)
  - Streaming APIs (encodeLines, decodeFromLines)
  - Round-trip validation
  - TypeScript type definitions included

**API Example:**
```javascript
import { encode, decode } from '@toon-format/toon';

// Encode with options
const toon = encode(data, {
  indent: 2,
  delimiter: '\t',  // Use tabs for better token efficiency
  lengthMarker: '#' // Optional: prefix array lengths with #
});

// Decode with strict validation
const json = decode(toonString, {
  strict: true,      // Validate structure (default: true)
  expandPaths: true  // Expand dotted keys (optional)
});
```

#### Python (In Development)
- **Package 1:** `toon-python` (PyPI)
- **Repository:** Community implementation
- **Status:** ⚠️ In Development (v0.1.2, Oct 2025)
- **Installation:** `pip install toon-python`
- **Features:**
  - Encoding only (no decoding yet)
  - Python type support (datetime, Decimal, UUID, bytes)
  - Configurable options
  - 30-60% token reduction

**API Example:**
```python
from toon_python import encode, EncodeOptions, Delimiter

data = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"}
    ]
}

# Basic encoding
toon_output = encode(data)

# With options
options = EncodeOptions(
    indent=2,
    delimiter=Delimiter.TAB,
    length_marker="#"
)
toon_output = encode(data, options)
```

**Limitations:**
- Encoding only (no decode functionality yet)
- Max dataset size: 10MB (configurable)
- No circular reference support
- Pure Python implementation (not optimized for speed)

- **Package 2:** `toon_format` (Official port in development)
- **Repository:** [toon-format/toon-format-python](https://github.com/toon-format)
- **Status:** 🚧 Under active development

### Other Official Implementations (In Development)

| Language | Status | Repository |
|----------|--------|------------|
| Go | 🚧 In Development | toon-go |
| Rust | 🚧 In Development | toon_format |
| .NET | 🚧 In Development | toon_format |
| Dart | 🚧 In Development | toon |
| Java | ✅ Available | JToon |
| Julia | ✅ Available | ToonFormat.jl |
| Swift | 🚧 In Development | toon-swift |

### Community Implementations

Active community ports available for:
- Apex, C++, Clojure, Crystal, Elixir, Gleam, Kotlin, Lua/Neovim, OCaml, Perl, PHP, R, Ruby, Scala

### CLI Tools

**Official CLI:**
```bash
# No installation needed (npx)
npx @toon-format/cli input.json -o output.toon

# Or install globally
npm install -g @toon-format/cli

# Convert JSON to TOON
toon encode input.json -o output.toon

# Convert TOON to JSON
toon decode input.toon -o output.json

# Show token statistics
toon encode input.json --stats
```

### Editor Support

- **VS Code:** Official extension - `vscode-toon` (syntax highlighting, validation, conversion)
- **Tree-sitter:** Grammar available for Neovim, Helix, Emacs, Zed
- **Neovim:** `toon.nvim` plugin
- **Other editors:** Use YAML syntax highlighting as approximation

### Library Maturity Assessment

**For Production Use:**
- ✅ **JavaScript/TypeScript:** Stable, battle-tested, feature-complete
- ⚠️ **Python:** Encoding only, development stage, limited features
- 🚧 **Other languages:** Most implementations are in development

**Recommendation for NRI News Brief:**
- **Backend (Python):** Use `toon-python` for encoding only; wait for decode support or implement custom parser
- **Frontend (JavaScript):** Use `@toon-format/toon` - fully stable and production-ready

---

## 6. Recommendation

### Should We Use TOON Format for NRI News Brief?

**Verdict: ⚠️ CONDITIONAL YES - with caveats**

### Strong Arguments FOR Using TOON

1. **Perfect Data Structure Match (80% score)**
   - News bulletins are **highly uniform arrays of objects** (title, summary, category, source, URL)
   - This is TOON's sweet spot: Expected 40-60% token savings
   - Tabular format: `bulletins[N]{title,summary,category,source,url}:`

2. **Token Optimization is Meaningful (90% score)**
   - 42 files × 40-60% token reduction = significant storage and transfer savings
   - Less data transferred to browser
   - If later integrating with LLMs (e.g., AI summarization, search), token efficiency directly reduces API costs

3. **JavaScript Support is Excellent (95% score)**
   - Stable, mature `@toon-format/toon` package
   - Small footprint, fast parsing, streaming support
   - Can bundle with Vite/Rollup or load via CDN
   - ES6 modules work seamlessly in vanilla JavaScript

4. **Human Readability (85% score)**
   - TOON files are easier to debug and inspect than minified JSON
   - Git diffs are cleaner (tabular rows vs JSON object spam)
   - Developers can manually edit if needed

5. **Growing Ecosystem (70% score)**
   - 20.7k GitHub stars, active development
   - Specification v3.0 is stable
   - Multi-language implementations emerging

### Strong Arguments AGAINST Using TOON

1. **Python Backend Support is Immature (CRITICAL - 40% score)**
   - `toon-python` is **encoding-only** (v0.1.2, Oct 2025)
   - No decode functionality = cannot parse TOON files in Python backend scripts
   - Would need to:
     - Wait for decode support (timeline unknown)
     - Implement custom Python parser (significant effort)
     - Use JSON as intermediate format (defeats purpose)
   - **This is a blocker for backend parsing scenarios**

2. **Ecosystem Risk (60% score)**
   - Format is only 1 year old (initial release ~2024)
   - Most language implementations are in development
   - Specification may evolve (currently v3.0, but "Working Draft" status)
   - Limited community support compared to JSON

3. **Tooling Maturity (65% score)**
   - No native browser/Python/Node.js support (unlike JSON)
   - Debugging tools are limited
   - Error messages may be less informative than JSON parsers
   - IDEs/editors have limited syntax support outside VS Code

4. **Complexity vs JSON (75% score)**
   - JSON is universal, zero-configuration
   - TOON requires bundled library on frontend
   - Extra dependency to maintain
   - Team needs to learn new format

5. **Overkill for Small Dataset (70% score)**
   - 42 files maximum (7 days × 6 bulletins/day)
   - Even with JSON, file sizes are manageable (probably <10-20 KB each)
   - Token savings matter more for large datasets or LLM API costs

### Recommended Approach: **START WITH JSON, MIGRATE TO TOON LATER IF NEEDED**

#### Phase 1: Initial Implementation (JSON)
- **Backend:** Python scripts generate JSON files from Perplexity API
- **Frontend:** Vanilla JavaScript loads and parses JSON (native support)
- **Storage:** Git repository with JSON files

**Rationale:**
- JSON is zero-risk, universal, no dependencies
- Python has full encode/decode support
- Establish baseline metrics (file sizes, performance)
- Ship faster with proven technology

#### Phase 2: Evaluate Migration (After 1-2 Weeks)
Measure actual metrics:
- Average file size in JSON
- Network transfer time to browser
- Storage repository size
- Whether LLM integration is planned

**Migration Triggers (any of these):**
- File sizes exceed 50 KB (token savings become meaningful)
- Planning to integrate LLM-based features (search, summarization, Q&A)
- Python decode support becomes available in `toon-python`
- Team comfortable with format, wants to optimize

#### Phase 3: Conditional Migration (TOON)
If metrics justify migration:
- **Backend:** Upgrade to `toon-python` with decode support OR implement custom parser
- **Frontend:** Switch to `@toon-format/toon` (minimal code changes)
- **Storage:** Convert existing JSON files to TOON format
- **Monitoring:** Compare before/after metrics

### Hybrid Approach (ALTERNATIVE)

**Generate both formats:**
```python
# Backend script
import json
from toon_python import encode  # encoding only

perplexity_data = fetch_news_from_perplexity()

# Save JSON for backend processing
with open('bulletin.json', 'w') as f:
    json.dump(perplexity_data, f)

# Save TOON for frontend consumption
toon_output = encode(perplexity_data)
with open('bulletin.toon', 'w') as f:
    f.write(toon_output)
```

**Frontend loads TOON:**
```javascript
import { decode } from '@toon-format/toon';

const response = await fetch('bulletin.toon');
const toonText = await response.text();
const data = decode(toonText);
```

**Benefits:**
- Backend uses JSON (full Python support)
- Frontend gets token-optimized TOON (faster transfers)
- Best of both worlds

**Cost:**
- Double storage (but files are small)
- Extra processing in backend script

### Final Recommendation Summary

| Aspect | Recommendation |
|--------|----------------|
| **Initial Implementation** | Use JSON (universal, zero-risk) |
| **Frontend Library** | Use `@toon-format/toon` IF migrating to TOON |
| **Backend Library** | Wait for `toon-python` decode support |
| **Migration Decision** | After 1-2 weeks with metrics |
| **Hybrid Approach** | Consider if token savings are critical now |

### Key Risks to Monitor

1. **Python decode support:** Check `toon-python` package updates
2. **Specification stability:** Monitor TOON spec changes (currently v3.0)
3. **Ecosystem maturity:** Watch for community adoption trends
4. **Performance vs JSON:** Benchmark actual file sizes and load times

### When to Definitely Use TOON

If any of these apply:
- ✅ File sizes regularly exceed 50 KB
- ✅ LLM integration is planned (token costs matter)
- ✅ Python decode support is available
- ✅ Team wants maximum optimization
- ✅ Storage/bandwidth costs are a concern

### When to Stick with JSON

If any of these apply:
- ❌ File sizes are small (<20 KB)
- ❌ No LLM integration planned
- ❌ Team unfamiliar with format
- ❌ Python decode support unavailable
- ❌ Need maximum compatibility/tooling

---

## References

- [TOON GitHub Repository](https://github.com/toon-format/toon)
- [TOON Specification v3.0](https://github.com/toon-format/spec)
- [TOON Format Website](https://toonformat.dev/)
- [JavaScript/TypeScript Package](https://www.npmjs.com/package/@toon-format/toon)
- [Python Package (toon-python)](https://pypi.org/project/toon-python/)
- [TOON Benchmarks](https://toonformat.dev/benchmarks)
- [JSON to TOON Converter (Online)](https://jsontotoon.com/)
- [TOON Documentation](https://jsontotoon.com/docs)

---

**Research Completed:** December 15, 2025  
**Status:** Ready for technical review and implementation decision
