export interface Category {
  value: string;
  label: string;
}

export interface City {
  value: string;
  label: string;
}

export interface Ad {
  id: string;
  title: string;
  description: string;
  price: number;
  category: string;
  city: string;
  contact_phone?: string;
  contact_email?: string;
  images?: string[];
  created_at?: string;
  updated_at?: string;
  expires_at?: string;
  views_count?: number;
  favorites_count?: number;
}
