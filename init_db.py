from app import db, create_app
from app.models.contracts import Supplier, Contract, Delivery, DeliveryItem
from datetime import datetime, date

app = create_app()

with app.app_context():
    # Створюємо всі таблиці
    db.create_all()
    
    # Додаємо тестового постачальника ФОП
    fop_supplier = Supplier(
        SupplierType='FOP',
        CompanyName="ФОП Петренко І.М.",
        ContactPerson="Петренко Іван Михайлович",
        Phone="+380501234567",
        Email="petrenko@example.com",
        Address="вул. Тестова 1, м. Київ",
        TaxNumber="1234567890",
        FOPNumber="123456789012345",
        FOPRegistrationDate=date(2020, 1, 1),
        IsActive=True
    )
    db.session.add(fop_supplier)
    
    # Додаємо тестового постачальника ТОВ
    tov_supplier = Supplier(
        SupplierType='TOV',
        CompanyName="ТОВ 'Тестова Компанія'",
        ContactPerson="Сидоренко Олександр Петрович",
        Phone="+380672345678",
        Email="info@testcompany.com",
        Address="вул. Бізнесова 10, м. Київ",
        TaxNumber="0987654321",
        EDRPOU="12345678",
        LegalForm="Товариство з обмеженою відповідальністю",
        DirectorName="Сидоренко Олександр Петрович",
        IsActive=True
    )
    db.session.add(tov_supplier)
    db.session.commit()
    
    # Додаємо тестовий контракт для ФОП
    fop_contract = Contract(
        SupplierID=fop_supplier.SupplierID,
        ContractNumber="CONTRACT-FOP-001",
        StartDate=date.today(),
        EndDate=date(2025, 12, 31),
        Description="Контракт з ФОП на поставку овочів",
        Status="active",
        TotalValue=50000.00,
        PaymentTerms="Передоплата 50%",
        DeliveryTerms="Самовивіз"
    )
    db.session.add(fop_contract)
    
    # Додаємо тестовий контракт для ТОВ
    tov_contract = Contract(
        SupplierID=tov_supplier.SupplierID,
        ContractNumber="CONTRACT-TOV-001",
        StartDate=date.today(),
        EndDate=date(2025, 12, 31),
        Description="Контракт з ТОВ на поставку напоїв",
        Status="active",
        TotalValue=150000.00,
        PaymentTerms="Відстрочка 30 днів",
        DeliveryTerms="Доставка"
    )
    db.session.add(tov_contract)
    db.session.commit()
    
    print("База даних успішно ініціалізована!") 