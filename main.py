class ParkingError(Exception):
    pass

class Driver:
    def __init__(self, name, id_number, vehicle):
        self._name = None
        self._id_number = None
        self.name = name
        self.id_number = id_number
        self._vehicle = vehicle

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, v):
        if not v.strip():
            raise ValueError("Invalid name")
        self._name = v.strip()

    @property
    def id_number(self):
        return self._id_number

    @id_number.setter
    def id_number(self, v):
        if not v.strip():
            raise ValueError("Invalid ID")
        self._id_number = v.strip()

    @property
    def vehicle(self):
        return self._vehicle


class Vehicle:
    def __init__(self, plate, vtype):
        self._plate = None
        self._type = None
        self.plate = plate
        self.type = vtype

    @property
    def plate(self):
        return self._plate

    @plate.setter
    def plate(self, v):
        t = v.strip().upper()
        if not t:
            raise ValueError("Invalid plate")
        self._plate = t

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, v):
        if not v.strip():
            raise ValueError("Invalid type")
        self._type = v.strip().lower()


class ParkingPass:
    def __init__(self, pid, driver):
        self._pid = pid
        self._driver = driver

    @property
    def pid(self):
        return self._pid

    @property
    def driver(self):
        return self._driver

    def calculate_fee(self, hours):
        raise NotImplementedError()


class StudentPass(ParkingPass):
    def __init__(self, pid, driver):
        super().__init__(pid, driver)
        self._rate = 2

    def calculate_fee(self, hours):
        return round(self._rate * hours, 2)


class StaffPass(ParkingPass):
    def __init__(self, pid, driver):
        super().__init__(pid, driver)
        self._rate = 3

    def calculate_fee(self, hours):
        return round(self._rate * hours, 2)


class ParkingLot:
    def __init__(self, name, capacity):
        self._name = name
        self._capacity = int(capacity)
        self._parked = set()

    def park(self, plate):
        if len(self._parked) >= self._capacity:
            raise ParkingError("Lot full")
        if plate in self._parked:
            raise ParkingError("Already parked")
        self._parked.add(plate)

    def remove(self, plate):
        if plate not in self._parked:
            raise ParkingError("Not parked")
        self._parked.remove(plate)

    def is_parked(self, plate):
        return plate in self._parked


class System:
    def __init__(self):
        self.drivers_by_id = {}
        self.drivers_by_plate = {}
        self.passes = {}
        self.lot = ParkingLot("Main Lot", 10)

    def register_driver(self, name, idn, plate, vtype):
        p = plate.upper()
        if p in self.drivers_by_plate:
            raise ParkingError("Plate exists")
        vehicle = Vehicle(p, vtype)
        driver = Driver(name, idn, vehicle)
        self.drivers_by_id[idn] = driver
        self.drivers_by_plate[p] = driver
        return driver

    def issue_pass(self, idn, ptype):
        if idn not in self.drivers_by_id:
            raise ParkingError("Driver not found")
        driver = self.drivers_by_id[idn]
        for ps in self.passes.values():
            if ps.driver.vehicle.plate == driver.vehicle.plate:
                raise ParkingError("This vehicle already has a pass")
        pid = str(uuid.uuid4())[:8]
        if ptype == "student":
            new = StudentPass(pid, driver)
        elif ptype == "staff":
            new = StaffPass(pid, driver)
        else:
            raise ParkingError("Unknown type")
        self.passes[pid] = new
        return new

    def get_pass(self, plate):
        for p in self.passes.values():
            if p.driver.vehicle.plate == plate:
                return p
        return None

    def park(self, plate):
        plate = plate.upper()
        if plate not in self.drivers_by_plate:
            raise ParkingError("Plate not registered")
        ps = self.get_pass(plate)
        if ps is None:
            raise ParkingError("No pass")
        self.lot.park(plate)

    def remove(self, plate, hours):
        plate = plate.upper()
        ps = self.get_pass(plate)
        if ps is None:
            raise ParkingError("No pass")
        self.lot.remove(plate)
        return ps.calculate_fee(hours)


def main():
    system = System()
    while True:
        print("\n1. Register driver and vehicle")
        print("2. Issue parking pass")
        print("3. Park a vehicle")
        print("4. Remove a vehicle and show fee")
        print("5. List all active passes")
        print("6. Exit")
        c = input("Choice: ").strip()

        try:
            if c == "1":
                name = input("Full name: ")
                idn = input("ID: ")
                plate = input("License plate: ")
                vtype = input("Vehicle type: ")
                d = system.register_driver(name, idn, plate, vtype)
                print("Driver registered:", d.name)

            elif c == "2":
                idn = input("Driver ID: ")
                t = input("Pass type (student/staff): ").lower()
                p = system.issue_pass(idn, t)
                print("Pass issued:", p.pid)

            elif c == "3":
                plate = input("Plate: ")
                system.park(plate)
                print("Vehicle parked")

            elif c == "4":
                plate = input("Plate: ")
                h = float(input("Hours parked: "))
                fee = system.remove(plate, h)
                print("Fee:", fee)

            elif c == "5":
                if not system.passes:
                    print("No active passes")
                else:
                    for pid, ps in system.passes.items():
                        print(pid, ps.driver.name, ps.driver.vehicle.plate)

            elif c == "6":
                break

            else:
                print("Invalid choice")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
