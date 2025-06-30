import { Component, OnInit } from '@angular/core';

import { MenuItem, MessageService } from 'primeng/api';
import { AuthService } from '../../../modules/auth/services/auth.service';

@Component({
  selector: 'app-header',
  standalone: false,
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
  providers: [MessageService],
})
export class HeaderComponent implements OnInit {
  items: MenuItem[] | undefined = undefined;
  avatarMenuItems: MenuItem[] = [];
  activeProject: string | null = null;
  isAuthenticated = false;

  constructor(
    private readonly _messageService: MessageService,
    private readonly _authService: AuthService
  ) {}

  ngOnInit(): void {
    // Check if user is authenticated
    this.isAuthenticated = this._authService.isAuthenticated();

    this.items = [
      {
        items: [
          {
            label: 'Create new project',
            styleClass: 'create-project',
          },
          {
            separator: true,
          },
        ],
      },
      {
        label: 'Projects',
        items: [
          {
            label: 'Launchpad',
            disabled: this.activeProject === 'Launchpad',
            command: () => this._switchProject('Launchpad'),
          },
          {
            label: 'Auctionify',
            disabled: this.activeProject === 'Auctionify',
            command: () => this._switchProject('Auctionify'),
          },
          {
            label: 'GameStore',
            disabled: this.activeProject === 'GameStore',
            command: () => this._switchProject('GameStore'),
          },
        ],
      },
    ];

    // Define avatar menu items
    this.avatarMenuItems = [
      {
        label: 'anora@dassyor.com', // Replace with dynamic user email if needed
        disabled: true,
        styleClass: 'user-email',
      },
      {
        separator: true,
      },
      {
        label: 'Settings',
        icon: 'pi pi-cog',
        command: () => this._navigateToSettings(),
      },
      {
        label: 'Support',
        icon: 'pi pi-comment',
        command: () => this._navigateToSupport(),
      },
      {
        label: 'About',
        icon: 'pi pi-info-circle',
        command: () => this._navigateToSupport(),
      },
      {
        label: 'Log out',
        icon: 'pi pi-sign-out',
        styleClass: 'log-out',
        command: () => this._logOut(),
      },
    ];
  }

  private _switchProject(projectName: string): void {
    this.activeProject = projectName;
    this._messageService.add({
      severity: 'success',
      summary: 'Success',
      detail: `Switched to ${projectName} project`,
      life: 3000,
    });

    // first remove the last item if it exists (2 including the separator)
    if (this.items && this.items.length > 2) {
      this.items.splice(this.items.length - 2, 2);
    }

    // then add the new project item
    if (this.items) {
      this.items.push(
        {
          separator: true,
        },
        {
          label: this.activeProject,
          items: [
            {
              label: 'Invite collaborators',
            },
            {
              label: 'Manage access',
            },
            {
              label: 'Rename project',
            },
            {
              label: 'Delete project',
              styleClass: 'delete-project',
            },
          ],
        }
      );
    }
  }

  private _navigateToSettings(): void {
    console.log('Navigating to settings...');
    // Add navigation logic here
  }

  private _navigateToSupport(): void {
    console.log('Navigating to support...');
    // Add navigation logic here
  }

  private _logOut(): void {
    this._authService.logout();
  }
}
