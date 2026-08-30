# SUBMISSION - Exit Exam MVC 1/2569 (อาทิตย์เช้า)

## 1. วิธีเปิดโปรแกรม
- ภาษา/เฟรมเวิร์ก: Python 3 (ทดสอบบน 3.11) ไม่ใช้ไลบรารีภายนอก
- Entry point / คำสั่งเปิดโปรแกรม: `python app.py` ส่วนติดต่อผู้ใช้เป็น Console แบบเมนู
- หมายเหตุที่จำเป็น (ถ้ามี):
  - รันชุดทดสอบ T1-T6 ด้วย `python -m unittest tests.test_scenarios -v`
  - ข้อความในโปรแกรมเป็นภาษาอังกฤษ ส่วนชื่อจาก `seed_data.json` แสดงตามข้อมูลจริง (ภาษาไทย) หากคอนโซลแสดงไม่ถูกให้สั่ง `chcp 65001` ก่อน
  - ข้อมูลเก็บในหน่วยความจำระหว่างการทำงานหนึ่งครั้ง ไม่เขียนทับ `seed_data.json`

## 2. ตารางเชื่อมโยง Requirements

| Requirement | Model / Domain | Controller / Action | View / Screen |
|---|---|---|---|
| R1 | `models/repository.py` (โหลด seed), `models/election.py` (สถานะ OPEN/CLOSED/FINALIZED), `models/errors.py` | `controllers/app_controller.py` (routing เมนูและเลือกบทบาท), `controllers/result.py` | `views/console_view.py` เมนูหลัก / เมนูผู้มีสิทธิ์ / เมนูเจ้าหน้าที่ |
| R2 | `Election.cast_ballot`, `Election._validate_ranking`, `models/ballot.py`, `models/voter.py` | `VotingController.candidates`, `VotingController.voters`, `VotingController.cast_ballot`, `AppController._cast_ballot` | `show_candidates`, `show_voters`, `ask_voter_id`, `ask_ranking`, `success` / `error` |
| R3 | `Election.close_voting`, `Election._group_duplicate_patterns`, `models/pattern_group.py` | `OfficerController.close_voting`, `AppController._close_voting` | `show_groups`, `show_status` (ผลชั่วคราว) |
| R4 | `Election.review_group`, `Election._finalize_when_all_reviewed`, `Election.scores`, `models/tally.py` | `OfficerController.review_group`, `OfficerController.pending_groups`, `ReportController.audit_rows`, `AppController._review_group` | `ask_group_id`, `ask_group_decision`, `show_audit`, `show_scores` |
| R5 | `Election.counted_ballots` / `rejected_ballots` / `under_review_ballots` / `pending_groups`, `RuleViolation` | `ReportController.snapshot`, การจับ `RuleViolation` แล้วคืน `Result.failure` ในทุก controller | `show_status`, `show_groups`, `show_scores`, `error` (ข้อความ `[REJECTED] ...`) |

## 3. ผลการทดสอบ

| กรณี | ผ่าน/ไม่ผ่าน | หมายเหตุ (เฉพาะที่จำเป็น) |
|---|---|---|
| T1 | ผ่าน | รับบัตร B04 ให้ V04 และ V04 เปลี่ยนเป็นใช้สิทธิ์แล้ว |
| T2 | ผ่าน | ปฏิเสธด้วยข้อความ `Voter V04 has already voted` จำนวนบัตรคงที่ 4 ใบ |
| T3 | ผ่าน | ปฏิเสธด้วยข้อความ `The 3 ranked candidates must all be different` และ V05 ยังไม่เสียสิทธิ์ |
| T4 | ผ่าน | รับบัตร B05 ให้ V05 |
| T5 | ผ่าน | สถานะเป็น Closed, กลุ่ม G01 (C01 > C02 > C03) 3 บัตรเข้าสถานะรอตรวจสอบ, ผลชั่วคราวจาก B03 และ B05 ได้ C04=4, C02=3, C03=2, C05=2, C01=1 |
| T6 | ผ่าน | รับรอง G01 แล้วสถานะเป็น Finalized คะแนนรวม C01=10, C02=9, C03=5, C04=4, C05=2 ตรงตามที่โจทย์กำหนด |

ทดสอบทั้งสองทาง: ผ่านเมนู CLI จริงในการรันครั้งเดียว และผ่าน `python -m unittest tests.test_scenarios` ซึ่งผ่าน 6 จาก 6 กรณี

## 4. ความแตกต่างระหว่างแบบที่ออกกับโปรแกรมจริง (ถ้ามี)
ระบุไม่เกิน 3 ข้อ
1. เพิ่มคลาส `Result` ในชั้น Controller ซึ่งไม่มีในแบบร่างแรก เพื่อให้ View รับผลลัพธ์เป็นข้อมูลธรรมดา แทนที่จะต้องจับ `RuleViolation` ข้ามชั้นเอง ทำให้ View ไม่รู้จักชนิดข้อผิดพลาดของ Model
2. `Repository` และ `Tally` ในแบบวาดเป็นคลาส แต่ในโปรแกรมทำเป็นโมดูลระดับฟังก์ชัน เพราะทั้งสองไม่มีสถานะของตัวเอง การทำเป็นคลาสจะเพิ่มชั้นโดยไม่ได้ประโยชน์
3. เพิ่ม `AppController` แยกจาก Controller ตามบทบาทสามตัว เพื่อให้การ routing เมนูไม่ปะปนกับตรรกะของฝั่งผู้มีสิทธิ์หรือฝั่งเจ้าหน้าที่

## 5. บันทึกการใช้ Generative AI

| เวลาโดยประมาณ | เครื่องมือ | ใช้เพื่ออะไร | นำคำแนะนำไปใช้อย่างไร |
|---|---|---|---|
| 09:37 | ChatGPT | ปรึกษาแนวคิดการวางโครงสร้าง MVC ที่ถูกต้อง และวิธีป้องกันไม่ให้ Controller ทำงานหนักเกิน | นำมาใช้ออกแบบโครงสร้างโฟลเดอร์ และแตก AppController เป็น controller ย่อย เช่นพวก Voting, Officer, Report แล้วจึงเริ่มเขียนโค้ด และ diagram คร่าวๆ เอง |
| 10:12 | ChatGPT | การทำ Clean Code สำหรับ OOP ถามหลักการทำ Encapsulation ใน Python และวิธีป้องกันไม่ให้คลาสอื่นมาแก้ไข List ภายในของ Object ได้โดยตรง | นำมาประยุกต์ใช้ในคลาส Election โดยซ่อนตัวแปรเป็น Private (_ballots) และใช้ @property รีเทิร์นค่าเป็น List copy |
| 10:41 | ChatGPT | ส่วน Algorithm และ Bug ถามวิธีเช็คว่าใน List มีค่าซ้ำกันหรือไม่ และทำไมถึงเกิด error unhashable type: list ตอนใช้เป็น key ใน Dictionary | นำมาแก้ bug ในฟังก์ชัน _validate_ranking โดยใช้ len(set()) และแก้ Bug group duplicate โดยแปลง list เป็น tuple |
| 11:29 | Gemini | ส่วนของการ Testing ถามวิธีเขียน Unit test เช็คว่าฟังก์ชันมีการโยน Exception raise error ออกมาตามที่คาดหวังหรือไม่ | นำมาเขียน test case assertRaises เพื่อทดสอบ RuleViolation ในกรณีโหวตซ้ำและใส่ candidate ซ้ำ เช่น test_t2_v04_cannot_vote_twice |
| 11:43 | ChatGPT | ส่วนของ Design ถามข้อดีข้อเสียของการใช้ Enum เทียบกับ String ธรรมดาในการจัดการสถานะ ของระบบ | นำมาสร้าง ElectionStatus และ BallotStatus เพื่อควบคุมสถานะการเปิด/ปิดโหวต และสถานะบัตร ให้ปลอดภัยจากการพิมพ์ผิด |
| ~12:00 | Gemini | ส่วนของ Algorithm ปรึกษาแนวทางการรวมคะแนน จาก List ของ Object อย่างมีประสิทธิภาพโดยไม่ต้องลูปซ้อนกันหลายชั้น | นำไอเดียมาใช้ในการคำนวณคะแนนโหวตร่วมกับ ranking_points เพื่อให้โค้ดทำงานได้เร็วและอ่านง่ายขึ้น |
| ~12:05 - 12:15 | Gemini | ปรึกษาวิธีรัน Unit test ทั้งหมดในโฟลเดอร์พร้อมกันผ่าน Command line และเช็คความเรียบร้อยของโค้ด | นำคำสั่ง `python -m unittest discover` มาใช้ test ทั้งหมดเพื่อตรวจสอบความถูกต้องเป็นครั้งสุดท้ายก่อนส่งงาน |
