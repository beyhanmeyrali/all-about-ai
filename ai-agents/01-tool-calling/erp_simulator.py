from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import uvicorn
import json
from enum import Enum

class ResponseState(Enum):
    ERROR = 'E'
    WARNING = 'W'
    SUCCESS = 'S'

class Response():
    status: ResponseState
    status_text:str
    json_data: str

    def __init__(self):
        self.status = None
        self.status_text = None
        self.json_data = None


class ErpDatabase():
    
    # Expanded sample data representing employees and their managers
    employees_data = [
        {"id": "1", "name": "John Doe", "manager_id": "2"},
        {"id": "2", "name": "Jane Smith", "manager_id": None},  # Manager 1
        {"id": "3", "name": "Emily Davis", "manager_id": "2"},
        {"id": "4", "name": "Michael Brown", "manager_id": "2"},
        {"id": "5", "name": "Alice Johnson", "manager_id": "3"},
        {"id": "6", "name": "David Wilson", "manager_id": "3"},
        {"id": "7", "name": "Chris Martin", "manager_id": None},  # Manager 2
        {"id": "8", "name": "Laura Garcia", "manager_id": "7"},
        {"id": "9", "name": "Daniel Lee", "manager_id": "7"},
        {"id": "10", "name": "Sarah Kim", "manager_id": "7"},
        {"id": "11", "name": "Peter Hall", "manager_id": "9"},
        {"id": "12", "name": "Nina Harris", "manager_id": "9"},
        {"id": "13", "name": "Tom Clark", "manager_id": None},  # Manager 3
        {"id": "14", "name": "Megan Lewis", "manager_id": "13"},
        {"id": "15", "name": "Olivia Walker", "manager_id": "13"},
        {"id": "16", "name": "James Young", "manager_id": "15"},
        {"id": "17", "name": "Sophia King", "manager_id": "15"},
        {"id": "18", "name": "Lucas Scott", "manager_id": "7"},
        {"id": "19", "name": "Grace Green", "manager_id": "7"}
    ]

     # Expanded payroll data with tax details
    payroll_data = [
        {"employee_id": "1", "salary": 50000, "bonus": 5000, "tax_rate": 0.25, "tax_amount": 12500},
        {"employee_id": "2", "salary": 60000, "bonus": 6000, "tax_rate": 0.30, "tax_amount": 18000},
        {"employee_id": "3", "salary": 55000, "bonus": 5500, "tax_rate": 0.27, "tax_amount": 14800},
        {"employee_id": "4", "salary": 52000, "bonus": 5200, "tax_rate": 0.26, "tax_amount": 13520},
        {"employee_id": "5", "salary": 48000, "bonus": 4800, "tax_rate": 0.24, "tax_amount": 11680},
        {"employee_id": "6", "salary": 47000, "bonus": 4700, "tax_rate": 0.23, "tax_amount": 10820},
        {"employee_id": "7", "salary": 60000, "bonus": 6000, "tax_rate": 0.30, "tax_amount": 18000},
        {"employee_id": "8", "salary": 45000, "bonus": 4500, "tax_rate": 0.22, "tax_amount": 9900},
        {"employee_id": "9", "salary": 49000, "bonus": 4900, "tax_rate": 0.25, "tax_amount": 12225},
        {"employee_id": "10", "salary": 46000, "bonus": 4600, "tax_rate": 0.24, "tax_amount": 11760},
        {"employee_id": "11", "salary": 55000, "bonus": 5500, "tax_rate": 0.27, "tax_amount": 14800},
        {"employee_id": "12", "salary": 53000, "bonus": 5300, "tax_rate": 0.26, "tax_amount": 13780},
        {"employee_id": "13", "salary": 62000, "bonus": 6200, "tax_rate": 0.32, "tax_amount": 20160},
        {"employee_id": "14", "salary": 51000, "bonus": 5100, "tax_rate": 0.25, "tax_amount": 12750},
        {"employee_id": "15", "salary": 50000, "bonus": 5000, "tax_rate": 0.24, "tax_amount": 12000},
        {"employee_id": "16", "salary": 47000, "bonus": 4700, "tax_rate": 0.23, "tax_amount": 10820},
        {"employee_id": "17", "salary": 45000, "bonus": 4500, "tax_rate": 0.22, "tax_amount": 9900},
        {"employee_id": "18", "salary": 46000, "bonus": 4600, "tax_rate": 0.23, "tax_amount": 11780},
        {"employee_id": "19", "salary": 44000, "bonus": 4400, "tax_rate": 0.21, "tax_amount": 10140}
    ]
    
    def get_employees_by_manager(self, manager_emp_id):
        resp = Response()

        # Find employees who report to the given manager_id
        employees = [emp for emp in self.employees_data if emp["manager_id"] == manager_emp_id]
        
        resp.json_data = json.dumps(employees, indent=4)

        if not employees:
            resp.status = ResponseState.WARNING
            resp.status_text = "No employees found for this manager."
        else:
            resp.status = ResponseState.SUCCESS
            resp.status_text = "found " + str(len(employees)) + " records"

        # Convert the list of employees to JSON format
        return resp


    def get_payroll_by_employee(self, employee_id):
        resp = Response()

        # Find payroll details for the given employee_id
        payroll = next((item for item in self.payroll_data if item["employee_id"] == employee_id), None)

        if payroll is None:
            resp.status = ResponseState.WARNING
            resp.status_text = "No payroll details found for this employee."
        else:
            resp.status = ResponseState.SUCCESS
            resp.status_text = "Payroll details found."

        # Convert the payroll details to JSON format
        resp.json_data = json.dumps(payroll, indent=4) if payroll else None

        return resp

    def update_payroll(self, employee_id, salary=None, bonus=None, tax_rate=None, tax_amount=None):
        resp = Response()

        # Find the payroll entry to update
        payroll_entry = next((item for item in self.payroll_data if item["employee_id"] == employee_id), None)

        if payroll_entry is None:
            resp.status = ResponseState.WARNING
            resp.status_text = "No payroll details found for this employee."
        else:
            # Update payroll details if provided
            if salary is not None:
                payroll_entry["salary"] = salary
            if bonus is not None:
                payroll_entry["bonus"] = bonus
            if tax_rate is not None:
                payroll_entry["tax_rate"] = tax_rate
            if tax_amount is not None:
                payroll_entry["tax_amount"] = tax_amount

            resp.status = ResponseState.SUCCESS
            resp.status_text = "Payroll details updated successfully."
            resp.json_data = json.dumps(payroll_entry, indent=4)

        return resp

app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

async def get_employees_of_manager(manager_emp_id: str):
    try:
        erp_db = ErpDatabase()
        response = erp_db.get_employees_by_manager(manager_emp_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_payroll_by_employee(employee_id: str):
    try:
        erp_db = ErpDatabase()
        response = erp_db.get_payroll_by_employee(employee_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_employees_of_manager/{manager_emp_id}")
async def get_emps_of_manager_get(manager_emp_id: str):
    return await get_employees_of_manager(manager_emp_id)

@app.post("/get_employees_of_manager")
async def get_emps_of_manager_post(query: Query):
    return await get_employees_of_manager(query.query)


@app.get("/get_payroll_by_employee/{employee_id}")
async def get_payroll_by_employee_get(employee_id: str):
    return await get_payroll_by_employee(employee_id)

@app.post("/get_payroll_by_employee")
async def get_payroll_by_employee_post(query: Query):
    return await get_payroll_by_employee(query.query)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
#http://127.0.0.1:8001/get_employees_of_manager/2
#http://127.0.0.1:8001/get_payroll_by_employee/7