1. The Scenario. Which one you chose, A to D, or your own domain written out as described under E.

Im going to do the Babson Bean Cafe. The Members information would be connected to Orders, Orders would be connected also to Pay and Reciept/Information about the individual order. Order info would be connected to the Menu/Availability. 

2. The ERD. Every table, its columns, its primary key and its foreign keys, and every relationship with both of its ends marked, as a mermaid erDiagram. Put it between a line ```mermaid and a line ```, as below, and VS Code's preview and GitHub both show it as a diagram. Chapter A of the SQL handbook, §5, shows how to read one.

```mermaid
erDiagram
    MEMBERS {
        int member_id PK
        string first_name
        string mobile_number
        string email "optional"
        date join_date
        int points_balance
    }

    PRODUCTS {
        int product_id PK
        string name
        string category "coffee, tea, food, or other"
        decimal price
        decimal cost
        boolean is_available
    }

    OPTIONS {
        int option_id PK
        string name
        decimal price
        decimal cost
    }

    ORDERS {
        int order_id PK
        datetime ordered_at
        int member_id FK "optional, null for non-members"
        string channel "counter or app"
    }

    ORDER_LINES {
        int line_id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price_charged "price on the day of sale"
    }

    LINE_OPTIONS {
        int line_id PK, FK
        int option_id PK, FK
        decimal price_charged "price on the day of sale"
    }

    PAYMENTS {
        int payment_id PK
        int order_id FK
        string method "cash, card, app, or points"
        decimal amount
    }

    MEMBERS |o--o{ ORDERS : places
    PRODUCTS ||--o{ ORDER_LINES : "sold as"
    ORDERS ||--|{ ORDER_LINES : contains
    ORDER_LINES ||--o{ LINE_OPTIONS : carries
    OPTIONS ||--o{ LINE_OPTIONS : "appears on"
    ORDERS ||--|{ PAYMENTS : "settled by"
```

3. What One Row Means. One sentence for each table, in the way Northwind's would read: "One row of orders is one order placed by one customer."

- One row of `members` is one loyalty member signed up at Babson Bean.
- One row of `products` is one item on the menu.
- One row of `options` is one add-on a drink can carry.
- One row of `orders` is one order placed by a customer, member or not.
- One row of `order_lines` is one product on one order, with the quantity bought and the price charged that day.
- One row of `line_options` is one option added to one order line, with the price charged that day.
- One row of `payments` is one payment made toward one order.

4. Design Choices. Four short answers, in your own words. Which key you chose where the business already had one, such as an email or a ticker, and why. Which relationships are optional, and what in the scenario tells you so. Which of the scenario's rules your tables cannot hold, and how you will check it instead. And one thing your agent proposed for the design that you changed or did not take, and why; if you designed it alone, one thing you checked in the ERD your agent drew.