export interface Product {
  title: string;
  price: string;
  price_num: number | null;
  image: string;
  link: string;
  rating: string;
  platform: string;
  score: number;
}

export interface Preferences {
  category: string | null;
  color: string | null;
  size: string | null;
  occasion: string | null;
  budget_max: number | null;
  brand: string | null;
}

export interface ChatResponse {
  status: string;
  intent: string;
  is_valid: boolean;
  preferences: Preferences;
  products: Product[];
  products_count: number;
  reflection_attempts: number;
  alert_id: string | null;
  response: string;
}

export interface Alert {
  id: string;
  product_name: string;
  brand: string | null;
  color: string | null;
  size: string | null;
  platform: string[];
  target_price: number | null;
  discount_pct: number | null;
  in_stock: boolean;
  new_arrival: boolean;
  is_active: boolean;
  triggered_at: string | null;
  created_at: string;
}

export interface AlertsResponse {
  status: string;
  user_id: string;
  total: number;
  alerts: Alert[];
}