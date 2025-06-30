import { NgModule } from '@angular/core';
import { CommonModule, NgOptimizedImage } from '@angular/common';
import { LayoutComponent } from './layout.component';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';
import { RouterModule } from '@angular/router';
import { MegaMenu } from 'primeng/megamenu';
import { Avatar } from 'primeng/avatar';
import { Badge } from 'primeng/badge';
import { Menu } from 'primeng/menu';
import { Button } from 'primeng/button';
import { ToastModule } from 'primeng/toast';
import { Sidebar } from 'primeng/sidebar';
import { Tooltip } from 'primeng/tooltip';

@NgModule({
  declarations: [LayoutComponent, HeaderComponent, FooterComponent],
  imports: [
    CommonModule,
    RouterModule,
    MegaMenu,
    Avatar,
    NgOptimizedImage,
    Badge,
    Menu,
    Button,
    ToastModule,
    Sidebar,
    Tooltip,
  ],
  exports: [LayoutComponent],
})
export class LayoutModule {}
