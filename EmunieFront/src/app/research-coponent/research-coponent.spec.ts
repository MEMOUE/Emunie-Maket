import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResearchCoponent } from './research-coponent';

describe('ResearchCoponent', () => {
  let component: ResearchCoponent;
  let fixture: ComponentFixture<ResearchCoponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResearchCoponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResearchCoponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
