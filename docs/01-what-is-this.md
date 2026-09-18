# What this project is (plain language)

You can give this file to a parent, a friend, or an examiner who is not a programmer.

## The real-world problem

When you buy a jar of honey or a bag of flour in India, the pack is supposed to say things like:

- how much it costs as **MRP** (the maximum price)
- how much is **inside** (500 g, 1 L, 5 kg)
- **who made it**
- **which country** it came from
- **when it was made** and **when it goes bad**

Those rules sit under **Legal Metrology** (plus food-pack rules). They exist so a shopper is not cheated.

On Amazon / Flipkart / Zepto, that information is often buried, paraphrased, or missing. A person cannot open ten thousand pages by hand.

## What the computer does

This project is a **first-pass helper**.

1. You give it a product page (or a photo, or pasted text).
2. It tries to **find those seven facts** in the words on the page.
3. It runs a **checklist of rules** (is MRP there? is origin there?).
4. It shows a **score**, the **evidence** (the exact words it used), and a list of **possible problems**.
5. A **human** clicks confirm or reject.
6. You can download a **PDF report**.

That is the whole product.

## What it is not

- **Not a lawyer.** It does not decide “this seller is guilty.”
- **Not ChatGPT.** It does not chat. It does not invent a country if the page never said one.
- **Not a hack of Amazon.** If Amazon shows a robot check, we stop and ask you to paste the text or use our fake shop **DemoMart**.
- **Not 100% on live websites.** The high AI numbers in the lab are on practice text we wrote, not on the whole internet.

The honest sentence for viva:

> This is a screening tool. A human still signs off. The machine only highlights what it can see.

## The seven fields

| Everyday name | Computer name |
|---|---|
| Product name | `product_name` |
| Maximum price | `mrp` |
| How much is in the pack | `net_quantity` |
| Who made / packed it | `manufacturer` |
| Country | `country_of_origin` |
| Made on | `manufacturing_date` |
| Use before | `expiry_date` |

If a field is missing, the status is `not_detected`.  
If two sources disagree (page says Rs. 100, photo says Rs. 120), the status is `ambiguous` — a human must look.

## The two shops

**DemoMart** is a fake Amazon-style shop we control: http://127.0.0.1:5000/demo/

Some listings use normal words (`MRP`, `Manufactured by`). A simple highlighter finds them.

Some listings use sneaky words (`Pack price`, `Plant operator`, `COO`). The highlighter misses them. The trained **NER** model is supposed to still find the numbers and names. That is the AI demo.

## One picture in your head

Think of a school exam:

- **Regex** is a strict teacher who only ticks the answer if you used the exact heading from the textbook.
- **NER** is a teacher who can still tick the answer if you wrote the same fact in different words.
- **Rules** are the marking scheme (must have MRP, must have origin…).
- **You** are the principal. You can override a mark.

## Where the code lives

GitHub: https://github.com/mav1730/LEGAL-METROLOGY-PROJECT  
On this PC: `C:\Users\admin\Documents\legal-metrology-compliance-checker`

Next: [02-how-the-machine-works.md](02-how-the-machine-works.md)
