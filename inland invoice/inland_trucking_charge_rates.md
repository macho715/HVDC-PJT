# Inland Trucking Charge Rate Table

Use this table as the **reference rate source** during invoice validation. Match on **Category + Port + Destination + Unit**.  
`Flag` column: `ok` (within ±30 %), `outlier` (deviation > 30 %), `missing` (rate not provided).

| Category   | Port              | Destination                 | Charge_Description                      | Unit      |   Rate_USD | Flag    |
|:-----------|:------------------|:----------------------------|:----------------------------------------|:----------|-----------:|:--------|
| Air        | Abu Dhabi Airport | MIRFA SITE                  | Inland Trucking (Upto 1ton)             | per truck |      150   | outlier |
| Air        | Abu Dhabi Airport | MIRFA SITE                  | Inland Trucking (Above 1ton, Upto 3ton) | per truck |      150   | outlier |
| Air        | Abu Dhabi Airport | MIRFA SITE                  | Inland Trucking (Above 3ton, Upto 5ton) | per truck |      180   | ok      |
| Air        | Abu Dhabi Airport | SHUWEIHAT Site              | Inland Trucking (Upto 1ton)             | per truck |      210   | ok      |
| Air        | Abu Dhabi Airport | SHUWEIHAT Site              | Inland Trucking (Above 1ton, Upto 3ton) | per truck |      210   | ok      |
| Air        | Abu Dhabi Airport | SHUWEIHAT Site              | Inland Trucking (Above 3ton, Upto 5ton) | per truck |      250   | ok      |
| Air        | Abu Dhabi Airport | Storage Yard                | Inland Trucking (Upto 1ton)             | per truck |      100   | outlier |
| Air        | Abu Dhabi Airport | Storage Yard                | Inland Trucking (Above 1ton, Upto 3ton) | per truck |      100   | outlier |
| Air        | Abu Dhabi Airport | Storage Yard                | Inland Trucking (Above 3ton, Upto 5ton) | per truck |      120   | outlier |
| Air        | Dubai Airport     | Hamariya free zone, Sharjah | Inland Trucking (Upto 1ton)             | per truck |      250   | ok      |
| Air        | Dubai Airport     | Hamariya free zone, Sharjah | Inland Trucking (Above 1ton, Upto 3ton) | per truck |      250   | ok      |
| Air        | Dubai Airport     | Hamariya free zone, Sharjah | Inland Trucking (Above 3ton, Upto 5ton) | per truck |      300   | ok      |
| Air        | Dubai Airport     | MIRFA SITE                  | Inland Trucking (Upto 1ton)             | per truck |      290   | ok      |
| Air        | Dubai Airport     | MIRFA SITE                  | Inland Trucking (Above 1ton, Upto 3ton) | per truck |      290   | ok      |
| Air        | Dubai Airport     | MIRFA SITE                  | Inland Trucking (Above 3ton, Upto 5ton) | per truck |      370   | outlier |
| Air        | Dubai Airport     | SHUWEIHAT Site              | Inland Trucking (Upto 1ton)             | per truck |      410   | outlier |
| Air        | Dubai Airport     | SHUWEIHAT Site              | Inland Trucking (Above 1ton, Upto 3ton) | per truck |      410   | outlier |
| Air        | Dubai Airport     | SHUWEIHAT Site              | Inland Trucking (Above 3ton, Upto 5ton) | per truck |      460   | outlier |
| Air        | Dubai Airport     | Storage Yard                | Inland Trucking (Upto 1ton)             | per truck |      200   | ok      |
| Air        | Dubai Airport     | Storage Yard                | Inland Trucking (Above 1ton, Upto 3ton) | per truck |      200   | ok      |
| Air        | Dubai Airport     | Storage Yard                | Inland Trucking (Above 3ton, Upto 5ton) | per truck |      250   | ok      |
| Bulk       | Jebel Ali Port    | Hamariya free zone, Sharjah | Inland Trucking                         | per RT    |       14   | ok      |
| Bulk       | Jebel Ali Port    | Hamariya free zone, Sharjah | Inland Trucking                         | per RT    |       19   | ok      |
| Bulk       | Jebel Ali Port    | MIRFA SITE                  | Inland Trucking                         | per RT    |       34.5 | outlier |
| Bulk       | Jebel Ali Port    | MIRFA SITE                  | Inland Trucking                         | per RT    |       20   | ok      |
| Bulk       | Jebel Ali Port    | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       44.5 | outlier |
| Bulk       | Jebel Ali Port    | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       25   | outlier |
| Bulk       | Jebel Ali Port    | Storage Yard                | Inland Trucking                         | per RT    |       15   | ok      |
| Bulk       | Jebel Ali Port    | Storage Yard                | Inland Trucking                         | per RT    |       19   | ok      |
| Bulk       | Khalifa Port      | MIRFA SITE                  | Inland Trucking                         | per RT    |       24.2 | outlier |
| Bulk       | Khalifa Port      | MIRFA SITE                  | Inland Trucking                         | per RT    |       13.4 | ok      |
| Bulk       | Khalifa Port      | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       29.2 | outlier |
| Bulk       | Khalifa Port      | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       15.2 | ok      |
| Bulk       | Khalifa Port      | Storage Yard                | Inland Trucking                         | per RT    |       10.5 | outlier |
| Bulk       | Khalifa Port      | Storage Yard                | Inland Trucking                         | per RT    |       12.4 | outlier |
| Bulk       | Mina Zayed Port   | MIRFA SITE                  | Inland Trucking                         | per RT    |       21   | ok      |
| Bulk       | Mina Zayed Port   | MIRFA SITE                  | Inland Trucking                         | per RT    |       11.6 | outlier |
| Bulk       | Mina Zayed Port   | MIRFA SITE                  | Inland Trucking                         | per RT    |       28.2 | outlier |
| Bulk       | Mina Zayed Port   | MIRFA SITE                  | Inland Trucking                         | per RT    |      nan   | missing |
| Bulk       | Mina Zayed Port   | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       25   | outlier |
| Bulk       | Mina Zayed Port   | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       13.1 | ok      |
| Bulk       | Mina Zayed Port   | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       34.7 | outlier |
| Bulk       | Mina Zayed Port   | SHUWEIHAT Site              | Inland Trucking                         | per RT    |      nan   | missing |
| Bulk       | Mina Zayed Port   | Storage Yard                | Inland Trucking                         | per RT    |        8.4 | outlier |
| Bulk       | Mina Zayed Port   | Storage Yard                | Inland Trucking                         | per RT    |       10.5 | outlier |
| Bulk       | Mina Zayed Port   | Storage Yard                | Inland Trucking                         | per RT    |       23.8 | ok      |
| Bulk       | Mina Zayed Port   | Storage Yard                | Inland Trucking                         | per RT    |      nan   | missing |
| Bulk       | Musaffah Port     | MIRFA SITE                  | Inland Trucking                         | per RT    |       18.4 | ok      |
| Bulk       | Musaffah Port     | MIRFA SITE                  | Inland Trucking                         | per RT    |       10.5 | outlier |
| Bulk       | Musaffah Port     | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       22.2 | ok      |
| Bulk       | Musaffah Port     | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       11.9 | outlier |
| Bulk       | Musaffah Port     | Storage Yard                | Inland Trucking                         | per RT    |        5.2 | outlier |
| Bulk       | Musaffah Port     | Storage Yard                | Inland Trucking                         | per RT    |        6.3 | outlier |
| Container  | Jebel Ali Port    | Hamariya free zone, Sharjah | Inland Trucking                         | per RT    |       55   | outlier |
| Container  | Jebel Ali Port    | Hamariya free zone, Sharjah | Inland Trucking                         | per truck |      400   | ok      |
| Container  | Jebel Ali Port    | Hamariya free zone, Sharjah | Inland Trucking                         | per truck |      400   | ok      |
| Container  | Jebel Ali Port    | MIRFA SITE                  | Inland Trucking                         | per RT    |       68   | outlier |
| Container  | Jebel Ali Port    | MIRFA SITE                  | Inland Trucking                         | per truck |      770   | outlier |
| Container  | Jebel Ali Port    | MIRFA SITE                  | Inland Trucking                         | per truck |      770   | outlier |
| Container  | Jebel Ali Port    | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       85   | outlier |
| Container  | Jebel Ali Port    | SHUWEIHAT Site              | Inland Trucking                         | per truck |      980   | outlier |
| Container  | Jebel Ali Port    | SHUWEIHAT Site              | Inland Trucking                         | per truck |      980   | outlier |
| Container  | Jebel Ali Port    | Storage Yard                | Inland Trucking                         | per RT    |       55   | outlier |
| Container  | Jebel Ali Port    | Storage Yard                | Inland Trucking                         | per truck |      400   | ok      |
| Container  | Jebel Ali Port    | Storage Yard                | Inland Trucking                         | per truck |      400   | ok      |
| Container  | Khalifa Port      | MIRFA SITE                  | Inland Trucking                         | per RT    |       35   | outlier |
| Container  | Khalifa Port      | MIRFA SITE                  | Inland Trucking                         | per truck |      496   | ok      |
| Container  | Khalifa Port      | MIRFA SITE                  | Inland Trucking                         | per truck |      496   | ok      |
| Container  | Khalifa Port      | Mina Zayed Port             | Inland Trucking                         | per RT    |       35   | outlier |
| Container  | Khalifa Port      | Mina Zayed Port             | Inland Trucking                         | per truck |      400   | ok      |
| Container  | Khalifa Port      | Mina Zayed Port             | Inland Trucking                         | per truck |      400   | ok      |
| Container  | Khalifa Port      | SHUWEIHAT Site              | Inland Trucking                         | per RT    |       45   | outlier |
| Container  | Khalifa Port      | SHUWEIHAT Site              | Inland Trucking                         | per truck |      679   | outlier |
| Container  | Khalifa Port      | SHUWEIHAT Site              | Inland Trucking                         | per truck |      679   | outlier |
| Container  | Khalifa Port      | Storage Yard                | Inland Trucking                         | per RT    |       29   | outlier |
| Container  | Khalifa Port      | Storage Yard                | Inland Trucking                         | per truck |      252   | outlier |
| Container  | Khalifa Port      | Storage Yard                | Inland Trucking                         | per truck |      252   | outlier |
