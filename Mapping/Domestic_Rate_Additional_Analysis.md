# 📊 Domestic Rate - 추가 분석 보고서 (PerKM, Vehicle, Fixed Cost)

## 1️⃣ Per Kilometer 요율 통계 (PerKM_Stats)
운행 구간별 거리 대비 요율(USD/km) 평균값 및 편차 통계입니다.

| Unnamed: 0   |       Value |
|:-------------|------------:|
| count        |  130        |
| mean         |   39.3012   |
| std          |  145.486    |
| min          |    0.833333 |
| 25%          |    2.4      |
| 50%          |    3.75     |
| 75%          |   20        |
| max          | 1500        |

## 2️⃣ 차량별 요약 (Vehicle_Summary)
차종별 평균 요율, 총 운행 거리, 총 트립 수 등의 통계 요약입니다.

| Vehicle Type          |   count |      mean |       min |        max |
|:----------------------|--------:|----------:|----------:|-----------:|
| 3 TON PU              |      14 |   5.33902 |  1        |   24       |
| Flatbed               |     100 |  26.0588  |  0.833333 |  529.081   |
| Flatbed - CICPA       |       1 |   4.61538 |  4.61538  |    4.61538 |
| Flatbed HAZMAT        |       1 |  47.651   | 47.651    |   47.651   |
| Flatbed(Side Grilled) |       2 |   2.4     |  2.4      |    2.4     |
| Lowbed                |       9 | 236.77    |  6.78857  | 1500       |
| Lowbed(1 X 14m)       |       1 |  57.5     | 57.5      |   57.5     |
| Lowbed(2 X 23m)       |       1 |  80       | 80        |   80       |

## 3️⃣ 비정상 고정요율 탐지 (FixedCost_Suspect)
고정 요율(Fixed Rate)이 비정상적으로 높은 항목을 탐지하여 정리한 테이블입니다.

|   No. | date                | Shipment Reference                   | Place of Loading   | Place of Delivery   | Vehicle Type   |   Distance(km) |   Rate (USD) |   per kilometer / usd | Flag                 |
|------:|:--------------------|:-------------------------------------|:-------------------|:--------------------|:---------------|---------------:|-------------:|----------------------:|:---------------------|
|     2 | 2024-10-01 00:00:00 | HVDC-ADOPT-SIM-0005                  | DSV MUSSAFAH YARD  | ESNAAD (MOSB)       | Flatbed        |             10 |       200    |                20     | Suspected Fixed Cost |
|    10 | 2024-10-01 00:00:00 | HVDC-DSV-MOSB-JETTY                  | ESNAAD (MOSB)      | JETTY               | Lowbed         |              5 |      1500    |               300     | Suspected Fixed Cost |
|    12 | 2024-10-01 00:00:00 | HVDC-DSV-MOSB-050                    | ESNAAD (MOSB)      | ESNAAD (MOSB)       | Flatbed        |              1 |       200    |               200     | Suspected Fixed Cost |
|    13 | 2024-10-01 00:00:00 | HVDC-DSV-MOSB-050                    | ESNAAD (MOSB)      | DSV MUSSAFAH YARD   | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|    14 | 2024-10-01 00:00:00 | HVDC-DSV-MOSB-050                    | DSV MUSSAFAH YARD  | ESNAAD (MOSB)       | Flatbed        |             10 |       200    |                20     | Suspected Fixed Cost |
|    22 | 2024-11-01 00:00:00 | HVDC-DSV-MOSB-052                    | MOSB               | DSV MUSSAFAH AYRD   | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|    23 | 2024-11-01 00:00:00 | HVDC-DSV-MOSB-052                    | DSV MUSSAFAH AYRD  | MOSB                | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|    24 | 2024-11-01 00:00:00 | HVDC-DSV-MOSB-057                    | DSV MUSSAFAH AYRD  | MOSB                | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|    26 | 2024-11-01 00:00:00 | HVDC-ADOPT-SIM-0005-2-MOSB           | DSV MUSAFFAH YARD  | MOSB                | Flatbed        |             10 |       200    |                20     | Suspected Fixed Cost |
|    27 | 2024-11-01 00:00:00 | Shifting of Basket                   | MOSB               | MOSB                | Flatbed        |              1 |       200    |               200     | Suspected Fixed Cost |
|    28 | 2024-11-01 00:00:00 | HVDC-DSV-DAS-SHIFTING                | DSV Musaffah Yard  | DSV MUSAFFAH YARD   | Flatbed        |              2 |       200    |               100     | Suspected Fixed Cost |
|    29 | 2024-11-01 00:00:00 | HVDC-DSV-SOC-CNT                     | MOSB               | MOSB                | Flatbed        |              1 |       200    |               200     | Suspected Fixed Cost |
|    37 | 2024-11-01 00:00:00 | HVDC-DSV-MIR-0031                    | DSV Musaffah Yard  | MOSB                | Flatbed        |             10 |       420    |                42     | Suspected Fixed Cost |
|    50 | 2024-11-01 00:00:00 | HVDC-DSV-MOSB-059                    | MOSB               | MOSB                | Lowbed         |              1 |      1500    |              1500     | Suspected Fixed Cost |
|    56 | 2024-11-01 00:00:00 | HVDC-SCT-RE-0001                     | Sharjah            | Jubail              | Flatbed        |             10 |      5290.81 |               529.081 | Suspected Fixed Cost |
|    57 | 2024-12-01 00:00:00 | HVDC-ADOPT-SIM-0005-2-MOSB           | DSV MUSAFFAH YARD  | MOSB                | Flatbed        |             10 |       200    |                20     | Suspected Fixed Cost |
|    58 | 2024-12-01 00:00:00 | Shifting of Basket                   | MOSB               | MOSB                | Flatbed        |              1 |       200    |               200     | Suspected Fixed Cost |
|    66 | 2024-12-01 00:00:00 | HVDC-DSV-DAS-SHIFTING                | DSV Musaffah Yard  | DSV MUSAFFAH YARD   | Flatbed        |              2 |       200    |               100     | Suspected Fixed Cost |
|    67 | 2024-12-01 00:00:00 | HVDC-DSV-SOC-CNT                     | MOSB               | MOSB                | Flatbed        |              1 |       200    |               200     | Suspected Fixed Cost |
|    70 | 2024-12-01 00:00:00 | HVDC-DSV-MIR-0031                    | DSV Musaffah Yard  | MOSB                | Flatbed        |             10 |       420    |                42     | Suspected Fixed Cost |
|    80 | 2025-02-01 00:00:00 | HVDC-ADOPT-SIM-0006-AAA              | AAA WAREHOUSE      | MOSB                | Flatbed HAZMAT |             10 |       476.51 |                47.651 | Suspected Fixed Cost |
|    82 | 2025-02-01 00:00:00 | HVDC-DAS-DSV-086                     | MINA FREEPORT      | MINA FREEPORT       | Flatbed        |              5 |       171    |                34.2   | Suspected Fixed Cost |
|    83 | 2025-02-01 00:00:00 | HVDC-ADOPT-SCT-0029-MOSB             | DSV MUSSAFAH YARD  | MOSB                | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|    87 | 2025-02-01 00:00:00 | HVDC-ADOPT-SCT-0037-MOSB             | DSV MUSSAFAH YARD  | MOSB                | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|    90 | 2025-02-01 00:00:00 | HVDC-DAS-NIE-MOSB-004                | DSV MUSSAFAH YARD  | MOSB                | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|   107 | 2025-02-01 00:00:00 | HVDC-DSV-FP-093                      | MINA FREEPORT      | MINA FREEPORT       | Lowbed         |              5 |       980.26 |               196.052 | Suspected Fixed Cost |
|   113 | 2025-03-01 00:00:00 | HVDC-ADOPT-SCT-0043, 0045, 0047-MOSB | DSV MUSSAFAH YARD  | MOSB                | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|   114 | 2025-03-01 00:00:00 | HVDC-ADOPT-SCT-0038,0039-MOSB        | DSV MUSSAFAH YARD  | MOSB                | Flatbed        |              5 |       200    |                40     | Suspected Fixed Cost |
|   118 | 2025-03-01 00:00:00 | HVDC-DSV-MOSB-SHU-097                | MOSB               | DSV MUSSAFAH YARD   | 3 TON PU       |              5 |       120    |                24     | Suspected Fixed Cost |
|   130 | 2025-03-01 00:00:00 | Mina Zayed Transformer               | MINA ZAYED         | MINA ZAYED          | nan            |              5 |       515.18 |               103.036 | Suspected Fixed Cost |