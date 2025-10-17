import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface DashboardStats {
  total_students: number;
  present_today: number;
  absent_today: number;
  late_today: number;
  attendance_rate: number;
  total_classes: number;
  total_sections: number;
  active_departments: number;
}

export interface AttendanceUpdate {
  type: 'attendance_update' | 'student_added' | 'class_update';
  data: any;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectInterval = 5000;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  private dashboardStatsSubject = new BehaviorSubject<DashboardStats | null>(null);
  private attendanceUpdatesSubject = new BehaviorSubject<AttendanceUpdate | null>(null);
  private connectionStatusSubject = new BehaviorSubject<boolean>(false);

  public dashboardStats$ = this.dashboardStatsSubject.asObservable();
  public attendanceUpdates$ = this.attendanceUpdatesSubject.asObservable();
  public connectionStatus$ = this.connectionStatusSubject.asObservable();

  constructor() {
    this.connect();
  }

  private connect(): void {
    try {
      const wsUrl = 'ws://localhost:8000/ws/dashboard/';
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = (event) => {
        console.log('WebSocket connected');
        this.connectionStatusSubject.next(true);
        this.reconnectAttempts = 0;
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected');
        this.connectionStatusSubject.next(false);
        this.handleReconnect();
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.connectionStatusSubject.next(false);
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.handleReconnect();
    }
  }

  private handleMessage(data: any): void {
    switch (data.type) {
      case 'dashboard_stats':
        this.dashboardStatsSubject.next(data.data);
        break;
      case 'attendance_update':
      case 'student_added':
      case 'class_update':
        this.attendanceUpdatesSubject.next({
          type: data.type,
          data: data.data
        });
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  public sendMessage(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  public requestDashboardStats(): void {
    this.sendMessage({
      type: 'get_dashboard_stats'
    });
  }

  public subscribeToClass(classId: number): void {
    this.sendMessage({
      type: 'subscribe_class',
      class_id: classId
    });
  }

  public subscribeToSection(sectionId: number): void {
    this.sendMessage({
      type: 'subscribe_section',
      section_id: sectionId
    });
  }

  public disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  ngOnDestroy(): void {
    this.disconnect();
  }
}