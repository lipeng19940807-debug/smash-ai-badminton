
import { bootstrapApplication } from '@angular/platform-browser';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, withHashLocation, Routes } from '@angular/router';
import { AppComponent } from './src/app.component';
import { LoginComponent } from './src/components/login/login.component';
import { DashboardComponent } from './src/components/dashboard/dashboard.component';
import { UploadComponent } from './src/components/upload/upload.component';
import { AnalysisComponent } from './src/components/analysis/analysis.component';
import { ReportComponent } from './src/components/report/report.component';
import { ShareComponent } from './src/components/share/share.component';

const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'upload', component: UploadComponent },
  { path: 'analysis', component: AnalysisComponent },
  { path: 'report', component: ReportComponent },
  { path: 'share', component: ShareComponent },
];

bootstrapApplication(AppComponent, {
  providers: [
    provideZonelessChangeDetection(),
    provideRouter(routes, withHashLocation())
  ]
}).catch(err => console.error(err));

// AI Studio always uses an `index.tsx` file for all project types.
