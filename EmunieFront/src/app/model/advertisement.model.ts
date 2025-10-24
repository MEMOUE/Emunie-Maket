export interface Advertisement {
  status: any;
  id?: number;
  user?: number;
  user_name?: string;
  title: string;
  link: string;
  image: string | File;
  image_url?: string;
  start_date: string;
  end_date?: string;
  duration_hours: number;
  duration_days?: number;
  total_price?: number;
  price_per_day: number;
  is_active?: boolean;
  is_approved?: boolean;
  is_running?: boolean;
  impressions?: number;
  clicks?: number;
  ctr?: number;
  created_at?: string;
}

export interface PaymentMethod {
  id: number;
  name: string;
  payment_type: string;
  provider?: string;
  logo?: string;
  is_active: boolean;
  processing_fee: number;
  order: number;
}

export interface AdvertisementTransaction {
  advertisement_id?: number;
  payment_method: number;
  phone_number?: string;
  total_amount?: number;
}

export interface PaymentResponse {
  transaction_id: number;
  reference: string;
  payment_url?: string;
  payment_instructions?: string;
  status: string;
}
