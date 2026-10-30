import csv
from pathlib import Path


COURSE_FEES = {"BCA": 45000, "BTech": 60000, "MBA": 80000}
FEE_FILE = Path(__file__).with_name("fees.txt")
students = []


def load_records():
    """Load valid student records from the fee file, creating it if needed.

    Invalid rows are skipped so a damaged line does not prevent the rest of
    the file from loading. The accepted row format is Roll,Name,Course,Paid.
    """
    path = Path(FEE_FILE)
    path.touch(exist_ok=True)
    records = []

    with path.open("r", newline="", encoding="utf-8") as fee_file:
        for row in csv.reader(fee_file):
            if len(row) != 4:
                continue
            try:
                roll = int(row[0].strip())
                name = row[1].strip()
                course = row[2].strip()
                paid = int(row[3].strip())
            except (TypeError, ValueError):
                continue

            if (
                roll <= 0
                or not name
                or course not in COURSE_FEES
                or paid < 0
                or paid > COURSE_FEES[course]
                or any(record["roll"] == roll for record in records)
            ):
                continue

            records.append(
                {"roll": roll, "name": name, "course": course, "paid": paid}
            )
    return records


def save_records(records=None):
    """Write all current records to the fee file."""
    if records is None:
        records = students
    path = Path(FEE_FILE)
    with path.open("w", newline="", encoding="utf-8") as fee_file:
        writer = csv.writer(fee_file, lineterminator="\n")
        for student in records:
            writer.writerow(
                [student["roll"], student["name"], student["course"], student["paid"]]
            )


def calculate_due(student):
    """Return the non-negative fee balance for one student."""
    return max(COURSE_FEES[student["course"]] - student["paid"], 0)


def get_status(student):
    """Return Paid, Partial, or Unpaid based on the fee balance."""
    due = calculate_due(student)
    if due == 0:
        return "Paid"
    if student["paid"] == 0:
        return "Unpaid"
    return "Partial"


def find_student(roll):
    """Find and return a student by roll number, or return None."""
    try:
        roll = int(roll)
    except (TypeError, ValueError):
        return None
    return next((student for student in students if student["roll"] == roll), None)


def _read_input(prompt):
    """Read one console value, returning None if input has ended."""
    try:
        return input(prompt).strip()
    except EOFError:
        return None


def add_student():
    """Prompt for and save a new student record."""
    raw_roll = _read_input("Roll number: ")
    if raw_roll is None:
        print("Input ended. Returning to menu.")
        return
    try:
        roll = int(raw_roll)
    except ValueError:
        print("Invalid roll number. Enter a numeric value.")
        return
    if roll <= 0:
        print("Roll number must be greater than zero.")
        return
    if find_student(roll) is not None:
        print("Roll number already exists.")
        return

    name = _read_input("Student name: ")
    if name is None:
        print("Input ended. Returning to menu.")
        return
    if not name:
        print("Name cannot be empty.")
        return

    course = _read_input("Course (BCA, BTech, MBA): ")
    if course is None:
        print("Input ended. Returning to menu.")
        return
    if course not in COURSE_FEES:
        print("Unknown course. Valid courses: BCA, BTech, MBA.")
        return

    student = {"roll": roll, "name": name, "course": course, "paid": 0}
    students.append(student)
    save_records()
    print(
        f"Student added: {roll} | {name} | {course} | Total Fee: {COURSE_FEES[course]} "
        f"| Paid: 0 | Due: {calculate_due(student)} | Status: {get_status(student)}"
    )


def pay_fee():
    """Prompt for a student and payment, rejecting invalid amounts."""
    raw_roll = _read_input("Roll number: ")
    if raw_roll is None:
        print("Input ended. Returning to menu.")
        return
    try:
        roll = int(raw_roll)
    except ValueError:
        print("Invalid roll number. Enter a numeric value.")
        return

    student = find_student(roll)
    if student is None:
        print(f"Unknown roll number: {roll}.")
        return

    raw_amount = _read_input("Payment amount: ")
    if raw_amount is None:
        print("Input ended. Returning to menu.")
        return
    try:
        amount = int(raw_amount)
    except ValueError:
        print("Invalid amount. Enter a numeric value.")
        return
    if amount <= 0:
        print("Payment amount must be greater than zero. Payment rejected.")
        return

    due = calculate_due(student)
    if amount > due:
        print(f"Amount exceeds due ({due}). Payment rejected.")
        return

    student["paid"] += amount
    save_records()
    print(
        f"Payment received. Paid: {student['paid']} | Due: {calculate_due(student)} "
        f"| Status: {get_status(student)}"
    )


def search_student():
    """Search by roll number and display the student's current fee record."""
    raw_roll = _read_input("Roll number: ")
    if raw_roll is None:
        print("Input ended. Returning to menu.")
        return
    try:
        roll = int(raw_roll)
    except ValueError:
        print("Invalid roll number. Enter a numeric value.")
        return

    student = find_student(roll)
    if student is None:
        print(f"Unknown roll number: {roll}.")
        return

    print(
        f"{student['roll']} | {student['name']} | {student['course']} | "
        f"Total Fee: {COURSE_FEES[student['course']]} | Paid: {student['paid']} | "
        f"Due: {calculate_due(student)} | Status: {get_status(student)}"
    )


def pending_dues():
    """Display each student with an outstanding balance."""
    pending = [student for student in students if calculate_due(student) > 0]
    if not pending:
        print("No pending dues.")
        return pending

    for student in pending:
        print(f"{student['roll']} | {student['name']} | Due: {calculate_due(student)}")
    return pending


def main():
    """Load records and run the console menu until the user exits."""
    global students
    students = load_records()

    while True:
        print("\nStudent Fee Management System")
        print("1) Add student")
        print("2) Pay fee")
        print("3) Search by roll number")
        print("4) Pending dues list")
        print("5) Exit")
        choice = _read_input("Choose an option: ")
        if choice is None:
            print("Input ended. Exiting.")
            break

        if choice == "1":
            add_student()
        elif choice == "2":
            pay_fee()
        elif choice == "3":
            search_student()
        elif choice == "4":
            pending_dues()
        elif choice == "5":
            print("Exiting Student Fee Management System.")
            break
        else:
            print("Invalid menu option. Choose 1 to 5.")


if __name__ == "__main__":
    main()
