export interface User {
    id: number
    name: string
    email: string
    role: 'admin' | 'client'
    is_active: boolean
    cedula?: string
    phone?: string
    is_kyc_verified?: boolean
}

export interface Institution {
    id: number
    name: string
    slogan?: string
    logo_path?: string
    address?: string
    phone?: string
    email?: string
    website?: string
    ruc?: string
    description?: string
}

export interface IndirectCharge {
    id: number
    name: string
    charge_type: string
    value: number
    is_percentage: boolean
    is_monthly: boolean
    is_active: boolean
    credit_type_id: number
}

export interface CreditType {
    id: number
    name: string
    category: string
    nominal_rate: number
    max_term_months?: number
    min_amount?: number
    max_amount?: number
    is_active: boolean
    institution_id?: number
    indirect_charges: IndirectCharge[]
}

export interface AmortizationRow {
    period: number
    initial_balance: number
    capital: number
    interest: number
    indirect_charges: Record<string, number>
    total_payment: number
    final_balance: number
}

export interface AmortizationResult {
    credit_type_name: string
    system: string
    amount: number
    term_months: number
    nominal_rate: number
    monthly_rate: number
    schedule: AmortizationRow[]
    charge_names: string[]
    total_capital: number
    total_interest: number
    total_charges: number
    total_charges_details: Record<string, number>
    total_payment: number
    schedule_id?: number
}

export interface InvestmentType {
    id: number
    name: string
    min_term_days: number
    max_term_days: number
    annual_rate: number
    min_amount?: number
    max_amount?: number
    payment_mode: string
    is_active: boolean
    institution_id?: number
}

export interface InvestmentResult {
    investment_type_name: string
    amount: number
    term_days: number
    annual_rate: number
    gross_interest: number
    ir_retention: number
    net_interest: number
    total_at_maturity: number
    simulation_id?: number
}

export interface InvestmentApplication {
    id: number
    investment_type_id: number
    amount: number
    term_days: number
    status: string
    biometric_status: string
    created_at?: string
}
