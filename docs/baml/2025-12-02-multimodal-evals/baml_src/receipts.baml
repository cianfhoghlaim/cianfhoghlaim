class Transaction {
  item_name string
  quantity int
  unit_price float
  unit_discount float?
  total_price float
}

class ReceiptData {
  transactions Transaction[]
  subtotal float?
  service_charge float?
  tax float?
  rounding float?
  discount_on_total float?
  grand_total float
}


function ExtractNumberOfTransactions(receipt_image: image) -> int {
  client Gemini25Flash
  prompt #"
  You are an expert at extracting the number of transactions from receipt images.
  
  Please carefully analyze this receipt image and extract the number of transactions. A transaction is any item that is purchased with an amount on the receipt. This does not include any subtotals, tips, taxes, rounding, or other amounts that are not a purchase.

  {{ ctx.output_format }}

  {{ _.role('user') }}
  {{ receipt_image }}
  "#
}

function ExtractReceiptTransactions(receipt_image: image) -> ReceiptData {
  client Gemini25Flash
  prompt #"
    You are an expert at extracting structured data from receipt images.
    
    Please analyze this receipt image and extract all the transaction details.
    
    For each item on the receipt, extract:
    - item_name: The name/description of the item
    - quantity: How many of this item were purchased
    - unit_price: The price per individual item (calculate from total_price / quantity if needed)
    - unit_discount: Any discount applied to the unit price (if present)
    - total_price: The total price for this line item
    
    Also extract the receipt totals:
    - subtotal: The subtotal before additional charges
    - service_charge: Any service fees (if present)
    - tax: Tax amount (if present, may be labeled as PB1, VAT, etc.)
    - rounding: Any rounding adjustments
    - grand_total: The final total amount
    - discount_on_total: Any discount applied to the grand total (if present)
    - currency: The currency used (infer from context if not explicitly shown)
    
    Be precise with numbers and make sure all extracted prices are accurate.
    If a field is not present or unclear, you can omit it (for optional fields) or use reasonable defaults.
    
    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ receipt_image }}
  "#
}



test recept {
  functions [ExtractReceiptTransactions]
  args {
    receipt_image {
      file "../data/cord-v2/images_and_metadata/larger_training_wheels/train_012.png"
    }
  }
}