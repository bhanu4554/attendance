import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface Student {
  id: number;
  user: {
    first_name: string;
    last_name: string;
    email: string;
    username: string;
  };
  roll_number: string;
  class_obj: {
    id: number;
    name: string;
    department: {
      name: string;
      code: string;
    };
  };
  section: {
    id: number;
    name: string;
  };
  date_of_birth: string;
  gender: string;
  blood_group: string;
  address: string;
  guardian_name: string;
  guardian_phone: string;
  guardian_email: string;
  admission_date: string;
  is_active: boolean;
}

interface Class {
  id: number;
  name: string;
  department: any;
  grade_level: number;
}

interface Section {
  id: number;
  name: string;
  class_obj: number;
  max_students: number;
  room_number: string;
}

@Component({
  selector: 'app-student-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `
    <div class="container-fluid">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="mb-0">Student Management</h2>
        <button class="btn btn-primary" (click)="showAddStudentModal = true">
          <i class="fas fa-plus"></i> Add Student
        </button>
      </div>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row">
            <div class="col-md-3">
              <label class="form-label">Class</label>
              <select class="form-select" [(ngModel)]="selectedClass" (change)="onClassChange()">
                <option value="">All Classes</option>
                <option *ngFor="let class of classes" [value]="class.id">
                  {{ class.name }} - {{ class.department.code }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Section</label>
              <select class="form-select" [(ngModel)]="selectedSection" (change)="filterStudents()">
                <option value="">All Sections</option>
                <option *ngFor="let section of availableSections" [value]="section.id">
                  {{ section.name }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Search</label>
              <input type="text" class="form-control" placeholder="Search students..." 
                     [(ngModel)]="searchTerm" (input)="filterStudents()">
            </div>
            <div class="col-md-3 d-flex align-items-end">
              <button class="btn btn-outline-secondary me-2" (click)="clearFilters()">
                <i class="fas fa-times"></i> Clear
              </button>
              <button class="btn btn-outline-primary" (click)="exportStudents()">
                <i class="fas fa-download"></i> Export
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Students Table -->
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">Students ({{ filteredStudents.length }})</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Roll Number</th>
                  <th>Student Name</th>
                  <th>Class</th>
                  <th>Section</th>
                  <th>Department</th>
                  <th>Email</th>
                  <th>Guardian</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let student of paginatedStudents">
                  <td>{{ student.roll_number }}</td>
                  <td>
                    <div>
                      <strong>{{ student.user.first_name }} {{ student.user.last_name }}</strong>
                      <br>
                      <small class="text-muted">{{ student.user.username }}</small>
                    </div>
                  </td>
                  <td>{{ student.class_obj.name }}</td>
                  <td>{{ student.section.name }}</td>
                  <td>{{ student.class_obj.department.code }}</td>
                  <td>{{ student.user.email }}</td>
                  <td>
                    <div>
                      <strong>{{ student.guardian_name }}</strong>
                      <br>
                      <small class="text-muted">{{ student.guardian_phone }}</small>
                    </div>
                  </td>
                  <td>
                    <span class="badge" [class]="student.is_active ? 'bg-success' : 'bg-danger'">
                      {{ student.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" (click)="viewStudent(student)">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button class="btn btn-outline-warning" (click)="editStudent(student)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button class="btn btn-outline-danger" (click)="deleteStudent(student)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr *ngIf="filteredStudents.length === 0">
                  <td colspan="9" class="text-center py-4">
                    <div class="text-muted">
                      <i class="fas fa-users fa-2x mb-3"></i>
                      <p>No students found</p>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <nav *ngIf="totalPages > 1">
            <ul class="pagination justify-content-center">
              <li class="page-item" [class.disabled]="currentPage === 1">
                <a class="page-link" (click)="changePage(currentPage - 1)">Previous</a>
              </li>
              <li class="page-item" *ngFor="let page of getPageNumbers()" 
                  [class.active]="page === currentPage">
                <a class="page-link" (click)="changePage(page)">{{ page }}</a>
              </li>
              <li class="page-item" [class.disabled]="currentPage === totalPages">
                <a class="page-link" (click)="changePage(currentPage + 1)">Next</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- Add Student Modal -->
    <div class="modal fade show d-block" *ngIf="showAddStudentModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add New Student</h5>
            <button type="button" class="btn-close" (click)="closeAddStudentModal()"></button>
          </div>
          <form [formGroup]="studentForm" (ngSubmit)="saveStudent()">
            <div class="modal-body">
              <div class="row">
                <!-- User Information -->
                <div class="col-md-6">
                  <h6 class="mb-3">Personal Information</h6>
                  <div class="mb-3">
                    <label class="form-label">First Name *</label>
                    <input type="text" class="form-control" formControlName="first_name">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Last Name *</label>
                    <input type="text" class="form-control" formControlName="last_name">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Email *</label>
                    <input type="email" class="form-control" formControlName="email">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Username *</label>
                    <input type="text" class="form-control" formControlName="username">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Date of Birth *</label>
                    <input type="date" class="form-control" formControlName="date_of_birth">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Gender *</label>
                    <select class="form-select" formControlName="gender">
                      <option value="">Select Gender</option>
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                    </select>
                  </div>
                </div>

                <!-- Academic Information -->
                <div class="col-md-6">
                  <h6 class="mb-3">Academic Information</h6>
                  <div class="mb-3">
                    <label class="form-label">Roll Number *</label>
                    <input type="text" class="form-control" formControlName="roll_number">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Class *</label>
                    <select class="form-select" formControlName="class_obj" (change)="onFormClassChange()">
                      <option value="">Select Class</option>
                      <option *ngFor="let class of classes" [value]="class.id">
                        {{ class.name }} - {{ class.department.code }}
                      </option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Section *</label>
                    <select class="form-select" formControlName="section">
                      <option value="">Select Section</option>
                      <option *ngFor="let section of formAvailableSections" [value]="section.id">
                        {{ section.name }}
                      </option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Blood Group</label>
                    <select class="form-select" formControlName="blood_group">
                      <option value="">Select Blood Group</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B-">B-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                    </select>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Address</label>
                    <textarea class="form-control" formControlName="address" rows="3"></textarea>
                  </div>
                </div>

                <!-- Guardian Information -->
                <div class="col-12">
                  <h6 class="mb-3">Guardian Information</h6>
                  <div class="row">
                    <div class="col-md-4">
                      <div class="mb-3">
                        <label class="form-label">Guardian Name *</label>
                        <input type="text" class="form-control" formControlName="guardian_name">
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="mb-3">
                        <label class="form-label">Guardian Phone *</label>
                        <input type="tel" class="form-control" formControlName="guardian_phone">
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="mb-3">
                        <label class="form-label">Guardian Email</label>
                        <input type="email" class="form-control" formControlName="guardian_email">
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" (click)="closeAddStudentModal()">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" [disabled]="studentForm.invalid">
                Save Student
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" *ngIf="showAddStudentModal"></div>
  `,
  styles: [`
    .modal.show {
      display: block !important;
    }
    
    .table th {
      background-color: #f8f9fa;
      font-weight: 600;
    }
    
    .btn-group-sm .btn {
      padding: 0.25rem 0.5rem;
    }
    
    .pagination .page-link {
      cursor: pointer;
    }
    
    .fa-2x {
      opacity: 0.5;
    }
  `]
})
export class StudentManagementComponent implements OnInit {
  students: Student[] = [];
  filteredStudents: Student[] = [];
  paginatedStudents: Student[] = [];
  classes: Class[] = [];
  sections: Section[] = [];
  availableSections: Section[] = [];
  formAvailableSections: Section[] = [];
  
  selectedClass: string = '';
  selectedSection: string = '';
  searchTerm: string = '';
  
  currentPage: number = 1;
  itemsPerPage: number = 10;
  totalPages: number = 0;
  
  showAddStudentModal: boolean = false;
  studentForm: FormGroup;
  
  private apiUrl = 'http://localhost:8000/api';

  constructor(
    private http: HttpClient,
    private formBuilder: FormBuilder
  ) {
    this.studentForm = this.formBuilder.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      username: ['', Validators.required],
      roll_number: ['', Validators.required],
      class_obj: ['', Validators.required],
      section: ['', Validators.required],
      date_of_birth: ['', Validators.required],
      gender: ['', Validators.required],
      blood_group: [''],
      address: [''],
      guardian_name: ['', Validators.required],
      guardian_phone: ['', Validators.required],
      guardian_email: ['']
    });
  }

  ngOnInit(): void {
    this.loadStudents();
    this.loadClasses();
    this.loadSections();
  }

  loadStudents(): void {
    this.http.get<Student[]>(`${this.apiUrl}/students/students/`).subscribe({
      next: (data) => {
        this.students = data;
        this.filterStudents();
      },
      error: (error) => {
        console.error('Error loading students:', error);
      }
    });
  }

  loadClasses(): void {
    this.http.get<Class[]>(`${this.apiUrl}/students/classes/`).subscribe({
      next: (data) => {
        this.classes = data;
      },
      error: (error) => {
        console.error('Error loading classes:', error);
      }
    });
  }

  loadSections(): void {
    this.http.get<Section[]>(`${this.apiUrl}/students/sections/`).subscribe({
      next: (data) => {
        this.sections = data;
      },
      error: (error) => {
        console.error('Error loading sections:', error);
      }
    });
  }

  filterStudents(): void {
    let filtered = [...this.students];

    if (this.selectedClass) {
      filtered = filtered.filter(s => s.class_obj.id.toString() === this.selectedClass);
    }

    if (this.selectedSection) {
      filtered = filtered.filter(s => s.section.id.toString() === this.selectedSection);
    }

    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(s => 
        s.user.first_name.toLowerCase().includes(term) ||
        s.user.last_name.toLowerCase().includes(term) ||
        s.roll_number.toLowerCase().includes(term) ||
        s.user.email.toLowerCase().includes(term)
      );
    }

    this.filteredStudents = filtered;
    this.totalPages = Math.ceil(this.filteredStudents.length / this.itemsPerPage);
    this.currentPage = 1;
    this.updatePaginatedStudents();
  }

  updatePaginatedStudents(): void {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    this.paginatedStudents = this.filteredStudents.slice(start, end);
  }

  onClassChange(): void {
    this.selectedSection = '';
    if (this.selectedClass) {
      this.availableSections = this.sections.filter(s => 
        s.class_obj.toString() === this.selectedClass
      );
    } else {
      this.availableSections = [];
    }
    this.filterStudents();
  }

  onFormClassChange(): void {
    const classId = this.studentForm.get('class_obj')?.value;
    this.studentForm.patchValue({ section: '' });
    
    if (classId) {
      this.formAvailableSections = this.sections.filter(s => 
        s.class_obj.toString() === classId
      );
    } else {
      this.formAvailableSections = [];
    }
  }

  clearFilters(): void {
    this.selectedClass = '';
    this.selectedSection = '';
    this.searchTerm = '';
    this.availableSections = [];
    this.filterStudents();
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.updatePaginatedStudents();
    }
  }

  getPageNumbers(): number[] {
    const pages: number[] = [];
    for (let i = 1; i <= this.totalPages; i++) {
      pages.push(i);
    }
    return pages;
  }

  closeAddStudentModal(): void {
    this.showAddStudentModal = false;
    this.studentForm.reset();
    this.formAvailableSections = [];
  }

  saveStudent(): void {
    if (this.studentForm.valid) {
      const formData = this.studentForm.value;
      
      this.http.post(`${this.apiUrl}/students/students/`, formData).subscribe({
        next: (response) => {
          console.log('Student created successfully:', response);
          this.closeAddStudentModal();
          this.loadStudents();
        },
        error: (error) => {
          console.error('Error creating student:', error);
        }
      });
    }
  }

  viewStudent(student: Student): void {
    console.log('View student:', student);
    // Implement view student functionality
  }

  editStudent(student: Student): void {
    console.log('Edit student:', student);
    // Implement edit student functionality
  }

  deleteStudent(student: Student): void {
    if (confirm(`Are you sure you want to delete ${student.user.first_name} ${student.user.last_name}?`)) {
      this.http.delete(`${this.apiUrl}/students/students/${student.id}/`).subscribe({
        next: () => {
          console.log('Student deleted successfully');
          this.loadStudents();
        },
        error: (error) => {
          console.error('Error deleting student:', error);
        }
      });
    }
  }

  exportStudents(): void {
    console.log('Export students');
    // Implement export functionality
  }
}