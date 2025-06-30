import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ErrorForbiddenComponent } from './error-forbidden.component';

describe('ErrorForbiddenComponent', () => {
  let component: ErrorForbiddenComponent;
  let fixture: ComponentFixture<ErrorForbiddenComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ErrorForbiddenComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ErrorForbiddenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
