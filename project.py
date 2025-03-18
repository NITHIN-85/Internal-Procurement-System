#!/usr/bin/env python3
import json
import os
import uuid
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# File paths for JSON storage
DATA_DIR = "data"
PURCHASES_FILE = os.path.join(DATA_DIR, "purchases.json")
VENDORS_FILE = os.path.join(DATA_DIR, "vendors.json")

# Initialize console for pretty output
console = Console()

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Helper functions for data operations
def load_data(file_path, default=None):
    """Load data from JSON file or return default if file doesn't exist."""
    if default is None:
        default = []
    
    if not os.path.exists(file_path):
        return default
    
    with open(file_path, 'r') as f:
        return json.load(f)

def save_data(file_path, data):
    """Save data to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Entity Classes
class Purchase:
    def __init__(self, item_name, quantity, requester, vendor_id=None, notes=""):
        self.id = str(uuid.uuid4())
        self.item_name = item_name
        self.quantity = quantity
        self.requester = requester
        self.vendor_id = vendor_id
        self.notes = notes
        self.status = "pending"  # pending, approved, rejected
        self.approver = None
        self.approval_date = None
        self.approval_notes = ""
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        purchase = cls(
            item_name=data['item_name'],
            quantity=data['quantity'],
            requester=data['requester'],
            vendor_id=data.get('vendor_id'),
            notes=data.get('notes', "")
        )
        purchase.id = data['id']
        purchase.status = data['status']
        purchase.approver = data.get('approver')
        purchase.approval_date = data.get('approval_date')
        purchase.approval_notes = data.get('approval_notes', "")
        purchase.created_at = data['created_at']
        purchase.updated_at = data['updated_at']
        return purchase

class Vendor:
    def __init__(self, name, contact_email, phone, address, price_rating, delivery_time, reviews=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.contact_email = contact_email
        self.phone = phone
        self.address = address
        self.price_rating = price_rating  # 1-10 scale (lower is cheaper)
        self.delivery_time = delivery_time  # Average delivery time in days
        self.reviews = reviews or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data):
        vendor = cls(
            name=data['name'],
            contact_email=data['contact_email'],
            phone=data['phone'],
            address=data['address'],
            price_rating=data['price_rating'],
            delivery_time=data['delivery_time'],
            reviews=data.get('reviews', [])
        )
        vendor.id = data['id']
        vendor.created_at = data['created_at']
        vendor.updated_at = data['updated_at']
        return vendor

# CRUD Operations for Purchase Requests
def create_purchase(item_name, quantity, requester, vendor_id=None, notes=""):
    purchase = Purchase(item_name, quantity, requester, vendor_id, notes)
    purchases = load_data(PURCHASES_FILE)
    purchases.append(purchase.to_dict())
    save_data(PURCHASES_FILE, purchases)
    return purchase

def get_purchase(purchase_id):
    purchases = load_data(PURCHASES_FILE)
    for p in purchases:
        if p['id'] == purchase_id:
            return Purchase.from_dict(p)
    return None

def update_purchase(purchase_id, updates):
    purchases = load_data(PURCHASES_FILE)
    for i, p in enumerate(purchases):
        if p['id'] == purchase_id:
            for key, value in updates.items():
                if key in p and key not in ['id', 'created_at']:
                    p[key] = value
            p['updated_at'] = datetime.now().isoformat()
            save_data(PURCHASES_FILE, purchases)
            return Purchase.from_dict(p)
    return None

def delete_purchase(purchase_id):
    purchases = load_data(PURCHASES_FILE)
    for i, p in enumerate(purchases):
        if p['id'] == purchase_id:
            del purchases[i]
            save_data(PURCHASES_FILE, purchases)
            return True
    return False

def list_purchases():
    return [Purchase.from_dict(p) for p in load_data(PURCHASES_FILE)]

# CRUD Operations for Vendors
def create_vendor(name, contact_email, phone, address, price_rating, delivery_time, reviews=None):
    vendor = Vendor(name, contact_email, phone, address, price_rating, delivery_time, reviews)
    vendors = load_data(VENDORS_FILE)
    vendors.append(vendor.to_dict())
    save_data(VENDORS_FILE, vendors)
    return vendor

def get_vendor(vendor_id):
    vendors = load_data(VENDORS_FILE)
    for v in vendors:
        if v['id'] == vendor_id:
            return Vendor.from_dict(v)
    return None

def update_vendor(vendor_id, updates):
    vendors = load_data(VENDORS_FILE)
    for i, v in enumerate(vendors):
        if v['id'] == vendor_id:
            for key, value in updates.items():
                if key in v and key not in ['id', 'created_at']:
                    v[key] = value
            v['updated_at'] = datetime.now().isoformat()
            save_data(VENDORS_FILE, vendors)
            return Vendor.from_dict(v)
    return None

def delete_vendor(vendor_id):
    vendors = load_data(VENDORS_FILE)
    for i, v in enumerate(vendors):
        if v['id'] == vendor_id:
            del vendors[i]
            save_data(VENDORS_FILE, vendors)
            return True
    return False

def list_vendors():
    return [Vendor.from_dict(v) for v in load_data(VENDORS_FILE)]

# Special Functions
def approve_purchase(purchase_id, approver, notes=""):
    """Approve a purchase request."""
    purchase = get_purchase(purchase_id)
    
    if not purchase:
        console.print(f"[bold red]Error:[/bold red] Purchase with ID {purchase_id} not found.")
        return None
    
    if purchase.status != "pending":
        console.print(f"[bold yellow]Warning:[/bold yellow] Purchase is already {purchase.status}.")
        return purchase
    
    # Update purchase to approved status
    updates = {
        "status": "approved",
        "approver": approver,
        "approval_date": datetime.now().isoformat(),
        "approval_notes": notes
    }
    
    purchase = update_purchase(purchase_id, updates)
    console.print(f"[bold green]Success:[/bold green] Purchase has been approved by {approver}!")
    
    return purchase

def reject_purchase(purchase_id, approver, notes=""):
    """Reject a purchase request."""
    purchase = get_purchase(purchase_id)
    
    if not purchase:
        console.print(f"[bold red]Error:[/bold red] Purchase with ID {purchase_id} not found.")
        return None
    
    if purchase.status != "pending":
        console.print(f"[bold yellow]Warning:[/bold yellow] Purchase is already {purchase.status}.")
        return purchase
    
    # Update purchase to rejected status
    updates = {
        "status": "rejected",
        "approver": approver,
        "approval_date": datetime.now().isoformat(),
        "approval_notes": notes
    }
    
    purchase = update_purchase(purchase_id, updates)
    console.print(f"[bold red]Note:[/bold red] Purchase has been rejected by {approver}.")
    
    return purchase

def compare_vendors(vendor_ids):
    """Evaluate vendors based on price, delivery time, and reviews."""
    vendors = []
    
    for vid in vendor_ids:
        vendor = get_vendor(vid)
        if vendor:
            vendors.append(vendor)
        else:
            console.print(f"[bold yellow]Warning:[/bold yellow] Vendor with ID {vid} not found.")
    
    if not vendors:
        console.print("[bold red]Error:[/bold red] No valid vendors to compare.")
        return
    
    # Create a comparison table
    table = Table(title="Vendor Comparison")
    
    table.add_column("Vendor", style="cyan")
    table.add_column("Price Rating", justify="center")
    table.add_column("Delivery Time (days)", justify="center")
    table.add_column("Avg. Review", justify="center")
    table.add_column("Overall Score", justify="center")
    
    for vendor in vendors:
        # Calculate average review score
        avg_review = 0
        if vendor.reviews:
            total = sum(review.get('rating', 0) for review in vendor.reviews)
            avg_review = total / len(vendor.reviews)
        
        # Calculate an overall score (lower is better)
        # 40% price, 40% delivery time, 20% reviews
        price_factor = vendor.price_rating / 10 * 0.4
        delivery_factor = min(vendor.delivery_time, 30) / 30 * 0.4
        review_factor = (5 - avg_review) / 5 * 0.2 if avg_review > 0 else 0.1
        
        overall_score = 10 - ((price_factor + delivery_factor + review_factor) * 10)
        overall_score = round(overall_score, 1)
        
        table.add_row(
            vendor.name,
            str(vendor.price_rating),
            str(vendor.delivery_time),
            f"{avg_review:.1f}" if vendor.reviews else "No reviews",
            f"{overall_score}"
        )
    
    console.print(table)
    
    # Recommend the best vendor (highest overall score)
    best_vendor = max(vendors, key=lambda v: 
        10 - ((v.price_rating / 10 * 0.4) + 
              (min(v.delivery_time, 30) / 30 * 0.4) + 
              ((5 - (sum(r.get('rating', 0) for r in v.reviews) / len(v.reviews) if v.reviews else 0)) / 5 * 0.2 if v.reviews else 0.1))
    )
    
    console.print(Panel(f"[bold green]Recommended Vendor:[/bold green] {best_vendor.name}", 
                        title="Recommendation", border_style="green"))

# Main CLI interface
def main():
    """Main function to run the procurement system."""
    console.print("[bold green]Internal Procurement System[/bold green]")
    
    # Initialize with sample data if empty
    if not os.path.exists(VENDORS_FILE):
        create_vendor("Acme Supplies", "contact@acme.com", "555-123-4567", 
                     "123 Main St, Anytown", 6.5, 3.5)
        create_vendor("MegaCorp", "sales@megacorp.com", "555-987-6543", 
                     "456 Business Ave, Commerce City", 4.2, 5.0)
    
    while True:
        console.print("\n[bold]Main Menu:[/bold]")
        console.print("1. Create Purchase Request")
        console.print("2. List Purchase Requests")
        console.print("3. Manage Vendors")
        console.print("4. Approve/Reject Purchase")
        console.print("5. Compare Vendors")
        console.print("0. Exit")
        
        choice = console.input("[bold cyan]Select an option:[/bold cyan] ")
        
        if choice == "1":
            item_name = console.input("[bold]Item name:[/bold] ")
            quantity = int(console.input("[bold]Quantity:[/bold] "))
            requester = console.input("[bold]Requester name:[/bold] ")
            
            # Show vendors for selection
            vendors = list_vendors()
            console.print("\n[bold]Available Vendors:[/bold]")
            for i, v in enumerate(vendors, 1):
                console.print(f"{i}. {v.name}")
            
            vendor_choice = console.input("\n[bold]Select vendor (number) or press Enter to skip:[/bold] ")
            vendor_id = None
            if vendor_choice.isdigit() and 0 < int(vendor_choice) <= len(vendors):
                vendor_id = vendors[int(vendor_choice) - 1].id
            
            notes = console.input("[bold]Notes:[/bold] ")
            purchase = create_purchase(item_name, quantity, requester, vendor_id, notes)
            console.print(f"[green]Purchase created with ID: {purchase.id}[/green]")
            
        elif choice == "2":
            purchases = list_purchases()
            
            if not purchases:
                console.print("[yellow]No purchase requests found.[/yellow]")
                continue
                
            table = Table(title="Purchase Requests")
            table.add_column("ID")
            table.add_column("Item")
            table.add_column("Quantity")
            table.add_column("Requester")
            table.add_column("Status")
            table.add_column("Approver")
            
            for p in purchases:
                table.add_row(
                    p.id, 
                    p.item_name, 
                    str(p.quantity), 
                    p.requester, 
                    p.status,
                    p.approver or "-"
                )
            
            console.print(table)
            
        elif choice == "3":
            # Vendor submenu
            console.print("\n[bold]Vendor Management:[/bold]")
            console.print("1. Add Vendor")
            console.print("2. List Vendors")
            console.print("3. Add Review to Vendor")
            
            vendor_choice = console.input("[bold cyan]Select option:[/bold cyan] ")
            
            if vendor_choice == "1":
                name = console.input("[bold]Vendor name:[/bold] ")
                email = console.input("[bold]Email:[/bold] ")
                phone = console.input("[bold]Phone:[/bold] ")
                address = console.input("[bold]Address:[/bold] ")
                
                try:
                    price = float(console.input("[bold]Price rating (1-10, lower is cheaper):[/bold] "))
                    delivery = float(console.input("[bold]Delivery time (days):[/bold] "))
                except ValueError:
                    console.print("[bold red]Error:[/bold red] Price and delivery time must be numbers.")
                    continue
                
                vendor = create_vendor(name, email, phone, address, price, delivery)
                console.print(f"[green]Vendor created with ID: {vendor.id}[/green]")
                
            elif vendor_choice == "2":
                vendors = list_vendors()
                
                if not vendors:
                    console.print("[yellow]No vendors found.[/yellow]")
                    continue
                    
                table = Table(title="Vendors")
                table.add_column("ID")
                table.add_column("Name")
                table.add_column("Price Rating")
                table.add_column("Delivery Time")
                table.add_column("Reviews")
                
                for v in vendors:
                    table.add_row(
                        v.id, 
                        v.name, 
                        str(v.price_rating), 
                        f"{v.delivery_time} days",
                        str(len(v.reviews))
                    )
                
                console.print(table)
                
            elif vendor_choice == "3":
                vendors = list_vendors()
                
                if not vendors:
                    console.print("[yellow]No vendors found.[/yellow]")
                    continue
                
                console.print("\n[bold]Available Vendors:[/bold]")
                for i, v in enumerate(vendors, 1):
                    console.print(f"{i}. {v.name}")
                
                try:
                    vendor_idx = int(console.input("[bold]Select vendor (number):[/bold] ")) - 1
                    if vendor_idx < 0 or vendor_idx >= len(vendors):
                        raise ValueError("Invalid vendor selection")
                    vendor = vendors[vendor_idx]
                    
                    rating = float(console.input("[bold]Rating (1-5):[/bold] "))
                    if rating < 1 or rating > 5:
                        raise ValueError("Rating must be between 1 and 5")
                        
                    comment = console.input("[bold]Comment:[/bold] ")
                    
                    review = {"rating": rating, "comment": comment, "date": datetime.now().isoformat()}
                    update_vendor(vendor.id, {"reviews": vendor.reviews + [review]})
                    console.print("[green]Review added![/green]")
                    
                except (ValueError, IndexError):
                    console.print("[bold red]Error:[/bold red] Invalid input.")
                
        elif choice == "4":
            purchases = list_purchases()
            pending = [p for p in purchases if p.status == "pending"]
            
            if not pending:
                console.print("[yellow]No pending purchases found.[/yellow]")
                continue
                
            table = Table(title="Pending Purchases")
            table.add_column("ID")
            table.add_column("Item")
            table.add_column("Quantity")
            table.add_column("Requester")
            
            for p in pending:
                table.add_row(p.id, p.item_name, str(p.quantity), p.requester)
            
            console.print(table)
            
            purchase_id = console.input("[bold]Enter Purchase ID to review:[/bold] ")
            purchase = get_purchase(purchase_id)
            
            if not purchase:
                console.print("[bold red]Error:[/bold red] Purchase not found.")
                continue
                
            if purchase.status != "pending":
                console.print(f"[bold yellow]Warning:[/bold yellow] Purchase is already {purchase.status}.")
                continue
                
            approver = console.input("[bold]Your name:[/bold] ")
            notes = console.input("[bold]Notes:[/bold] ")
            
            decision = console.input("[bold]Approve or Reject? (A/R):[/bold] ").upper()
            
            if decision == "A":
                approve_purchase(purchase_id, approver, notes)
            elif decision == "R":
                reject_purchase(purchase_id, approver, notes)
            else:
                console.print("[bold red]Error:[/bold red] Invalid choice. Please enter A or R.")
            
        elif choice == "5":
            vendors = list_vendors()
            
            if len(vendors) < 2:
                console.print("[yellow]Need at least 2 vendors to compare.[/yellow]")
                continue
                
            console.print("\n[bold]Available Vendors:[/bold]")
            for i, v in enumerate(vendors, 1):
                console.print(f"{i}. {v.name}")
                
            vendor_indices = console.input("[bold]Enter vendor numbers to compare (comma-separated):[/bold] ")
            try:
                indices = [int(idx.strip()) - 1 for idx in vendor_indices.split(",")]
                vendor_ids = [vendors[idx].id for idx in indices if 0 <= idx < len(vendors)]
                
                if len(vendor_ids) < 2:
                    console.print("[bold red]Error:[/bold red] Please select at least 2 valid vendors.")
                    continue
                    
                compare_vendors(vendor_ids)
                
            except (ValueError, IndexError):
                console.print("[bold red]Error:[/bold red] Invalid input. Please enter valid vendor numbers.")
            
        elif choice == "0":
            console.print("[green]Thank you for using the procurement system. Goodbye![/green]")
            break
            
        else:
            console.print("[red]Invalid option. Please try again.[/red]")

if __name__ == "__main__":
    main()
