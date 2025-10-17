import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { WebSocketService, DashboardStats, AttendanceUpdate } from '../../services/websocket.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container-fluid">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="mb-0">Smart Attendance Dashboard</h2>
        <div class="d-flex align-items-center">
          <span class="badge me-2" [class]="connectionStatus ? 'bg-success' : 'bg-danger'">
            {{ connectionStatus ? 'Connected' : 'Disconnected' }}
          </span>
          <button class="btn btn-sm btn-outline-primary" (click)="refreshStats()">
            <i class="fas fa-sync-alt"></i> Refresh
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4" *ngIf="dashboardStats">
        <div class="col-md-3 col-sm-6 mb-3">
          <div class="card bg-primary text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="mb-0">{{ dashboardStats.total_students }}</h4>
                  <p class="mb-0">Total Students</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-users fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3 col-sm-6 mb-3">
          <div class="card bg-success text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="mb-0">{{ dashboardStats.present_today }}</h4>
                  <p class="mb-0">Present Today</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-check-circle fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3 col-sm-6 mb-3">
          <div class="card bg-danger text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="mb-0">{{ dashboardStats.absent_today }}</h4>
                  <p class="mb-0">Absent Today</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-times-circle fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-3 col-sm-6 mb-3">
          <div class="card bg-warning text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div>
                  <h4 class="mb-0">{{ dashboardStats.late_today }}</h4>
                  <p class="mb-0">Late Today</p>
                </div>
                <div class="align-self-center">
                  <i class="fas fa-clock fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Attendance Rate -->
      <div class="row mb-4" *ngIf="dashboardStats">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Overall Attendance Rate</h5>
            </div>
            <div class="card-body text-center">
              <div class="progress mb-3" style="height: 30px;">
                <div class="progress-bar" 
                     [style.width.%]="dashboardStats.attendance_rate"
                     [class]="getAttendanceRateClass(dashboardStats.attendance_rate)">
                  {{ dashboardStats.attendance_rate.toFixed(1) }}%
                </div>
              </div>
              <p class="text-muted mb-0">
                {{ dashboardStats.present_today + dashboardStats.late_today }} out of {{ dashboardStats.total_students }} students present
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">System Overview</h5>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-4">
                  <h3 class="text-info">{{ dashboardStats.active_departments }}</h3>
                  <p class="text-muted mb-0">Departments</p>
                </div>
                <div class="col-4">
                  <h3 class="text-info">{{ dashboardStats.total_classes }}</h3>
                  <p class="text-muted mb-0">Classes</p>
                </div>
                <div class="col-4">
                  <h3 class="text-info">{{ dashboardStats.total_sections }}</h3>
                  <p class="text-muted mb-0">Sections</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Real-time Updates -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Real-time Updates</h5>
              <small class="text-muted">Last updated: {{ lastUpdateTime | date:'medium' }}</small>
            </div>
            <div class="card-body">
              <div *ngIf="realtimeUpdates.length === 0" class="text-center text-muted py-4">
                <i class="fas fa-clock fa-2x mb-3"></i>
                <p>Waiting for real-time updates...</p>
              </div>
              
              <div *ngFor="let update of realtimeUpdates; let i = index" 
                   class="alert alert-dismissible fade show"
                   [class]="getUpdateAlertClass(update.type)">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ getUpdateTitle(update.type) }}</strong>
                    <p class="mb-0">{{ getUpdateMessage(update) }}</p>
                  </div>
                  <small class="text-muted">{{ update.timestamp | date:'shortTime' }}</small>
                </div>
                <button type="button" class="btn-close" (click)="removeUpdate(i)"></button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .card {
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      border: none;
      border-radius: 8px;
    }
    
    .progress-bar {
      font-weight: bold;
      transition: width 0.5s ease-in-out;
    }
    
    .alert {
      margin-bottom: 0.5rem;
    }
    
    .badge {
      font-size: 0.75rem;
    }
    
    .fa-2x {
      opacity: 0.7;
    }
    
    .card-body h3 {
      margin-bottom: 0.25rem;
    }
  `]
})
export class DashboardComponent implements OnInit, OnDestroy {
  dashboardStats: DashboardStats | null = null;
  connectionStatus: boolean = false;
  realtimeUpdates: any[] = [];
  lastUpdateTime: Date = new Date();
  
  private subscriptions: Subscription[] = [];

  constructor(private webSocketService: WebSocketService) {}

  ngOnInit(): void {
    // Subscribe to dashboard stats
    this.subscriptions.push(
      this.webSocketService.dashboardStats$.subscribe(stats => {
        if (stats) {
          this.dashboardStats = stats;
          this.lastUpdateTime = new Date();
        }
      })
    );

    // Subscribe to connection status
    this.subscriptions.push(
      this.webSocketService.connectionStatus$.subscribe(status => {
        this.connectionStatus = status;
      })
    );

    // Subscribe to real-time updates
    this.subscriptions.push(
      this.webSocketService.attendanceUpdates$.subscribe(update => {
        if (update) {
          this.addRealtimeUpdate(update);
        }
      })
    );

    // Request initial dashboard stats
    this.refreshStats();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  refreshStats(): void {
    this.webSocketService.requestDashboardStats();
  }

  addRealtimeUpdate(update: AttendanceUpdate): void {
    const updateWithTimestamp = {
      ...update,
      timestamp: new Date()
    };
    
    this.realtimeUpdates.unshift(updateWithTimestamp);
    
    // Keep only last 10 updates
    if (this.realtimeUpdates.length > 10) {
      this.realtimeUpdates = this.realtimeUpdates.slice(0, 10);
    }
  }

  removeUpdate(index: number): void {
    this.realtimeUpdates.splice(index, 1);
  }

  getAttendanceRateClass(rate: number): string {
    if (rate >= 90) return 'bg-success';
    if (rate >= 75) return 'bg-warning';
    return 'bg-danger';
  }

  getUpdateAlertClass(type: string): string {
    switch (type) {
      case 'attendance_update': return 'alert-info';
      case 'student_added': return 'alert-success';
      case 'class_update': return 'alert-warning';
      default: return 'alert-secondary';
    }
  }

  getUpdateTitle(type: string): string {
    switch (type) {
      case 'attendance_update': return 'Attendance Updated';
      case 'student_added': return 'New Student Added';
      case 'class_update': return 'Class Information Updated';
      default: return 'System Update';
    }
  }

  getUpdateMessage(update: any): string {
    switch (update.type) {
      case 'attendance_update':
        return `${update.data.student_name} marked as ${update.data.status}`;
      case 'student_added':
        return `${update.data.student_name} has been added to ${update.data.class_name}`;
      case 'class_update':
        return `Class ${update.data.class_name} information has been updated`;
      default:
        return 'System has been updated';
    }
  }
}