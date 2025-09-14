# BuyBuy E-Commerce Database Schema

## Database Overview

The BuyBuy e-commerce system uses MySQL 8.0 as the primary database. The schema is designed for high performance, scalability, and data integrity with proper indexing and relationships.

## Database Configuration

### MySQL Version

- **Version**: MySQL 8.0+
- **Engine**: InnoDB (for ACID compliance and foreign key support)
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci

### Connection Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'buybuy_db',
        'USER': 'buybuy_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

## Table Definitions

### 1. Users Table

Stores user account information and authentication data.

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_username (username),
    INDEX idx_users_email (email),
    INDEX idx_users_is_active (is_active),
    INDEX idx_users_date_joined (date_joined)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 2. User Profiles Table

Stores additional user profile information.

```sql
CREATE TABLE user_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    phone VARCHAR(20) NULL,
    address TEXT NULL,
    city VARCHAR(100) NULL,
    state VARCHAR(100) NULL,
    country VARCHAR(100) NULL,
    postal_code VARCHAR(20) NULL,
    date_of_birth DATE NULL,
    avatar_url VARCHAR(500) NULL,
    bio TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_profile (user_id),
    INDEX idx_user_profiles_user_id (user_id),
    INDEX idx_user_profiles_country (country),
    INDEX idx_user_profiles_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3. Categories Table

Stores product categories with hierarchical structure.

```sql
CREATE TABLE categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    parent_id BIGINT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INT NOT NULL DEFAULT 0,
    meta_title VARCHAR(200) NULL,
    meta_description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_categories_slug (slug),
    INDEX idx_categories_parent_id (parent_id),
    INDEX idx_categories_is_active (is_active),
    INDEX idx_categories_sort_order (sort_order),
    INDEX idx_categories_name (name),
    INDEX idx_categories_parent_active (parent_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 4. Products Table

Stores product information and inventory data.

```sql
CREATE TABLE products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(300) NOT NULL,
    description TEXT NULL,
    short_description VARCHAR(500) NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    compare_price DECIMAL(10,2) NULL,
    cost_price DECIMAL(10,2) NULL,
    category_id BIGINT NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 5,
    weight DECIMAL(8,2) NULL,
    dimensions VARCHAR(100) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_digital BOOLEAN NOT NULL DEFAULT FALSE,
    requires_shipping BOOLEAN NOT NULL DEFAULT TRUE,
    tax_class VARCHAR(50) NULL,
    meta_title VARCHAR(200) NULL,
    meta_description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_products_sku (sku),
    INDEX idx_products_category_id (category_id),
    INDEX idx_products_price (price),
    INDEX idx_products_is_active (is_active),
    INDEX idx_products_is_featured (is_featured),
    INDEX idx_products_stock_quantity (stock_quantity),
    INDEX idx_products_created_at (created_at),
    INDEX idx_products_category_active (category_id, is_active),
    INDEX idx_products_price_active (price, is_active),
    INDEX idx_products_name (name),
    FULLTEXT idx_products_search (name, description, short_description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5. Product Images Table

Stores product image information.

```sql
CREATE TABLE product_images (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(200) NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INT NOT NULL DEFAULT 0,
    file_size INT NULL,
    width INT NULL,
    height INT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_images_product_id (product_id),
    INDEX idx_product_images_is_primary (is_primary),
    INDEX idx_product_images_sort_order (sort_order),
    INDEX idx_product_images_product_primary (product_id, is_primary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6. Product Specifications Table

Stores product specifications and attributes.

```sql
CREATE TABLE product_specifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    specification_name VARCHAR(200) NOT NULL,
    specification_value TEXT NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_specifications_product_id (product_id),
    INDEX idx_product_specifications_name (specification_name),
    INDEX idx_product_specifications_sort_order (sort_order),
    INDEX idx_product_specifications_product_sort (product_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 7. JWT Tokens Table

Stores JWT refresh tokens for authentication.

```sql
CREATE TABLE jwt_tokens (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_jwt_tokens_user_id (user_id),
    INDEX idx_jwt_tokens_token_hash (token_hash),
    INDEX idx_jwt_tokens_expires_at (expires_at),
    INDEX idx_jwt_tokens_is_revoked (is_revoked),
    INDEX idx_jwt_tokens_user_expires (user_id, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 8. Audit Logs Table

Stores audit trail for important operations.

```sql
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id BIGINT NULL,
    old_values JSON NULL,
    new_values JSON NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_action (action),
    INDEX idx_audit_logs_resource_type (resource_type),
    INDEX idx_audit_logs_resource_id (resource_id),
    INDEX idx_audit_logs_created_at (created_at),
    INDEX idx_audit_logs_user_action (user_id, action),
    INDEX idx_audit_logs_resource (resource_type, resource_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Indexing Strategy

### Primary Indexes

All tables have auto-incrementing primary keys with clustered indexes.

### Secondary Indexes

- **Foreign Key Indexes**: All foreign key columns are indexed for join optimization
- **Unique Indexes**: Email, username, SKU, and slug fields have unique indexes
- **Search Indexes**: Name fields and searchable text fields are indexed
- **Status Indexes**: Boolean fields like `is_active`, `is_featured` are indexed
- **Date Indexes**: `created_at` and `updated_at` fields are indexed for sorting

### Composite Indexes

- **Products**: `(category_id, is_active)` for category filtering
- **Products**: `(price, is_active)` for price-based queries
- **Categories**: `(parent_id, is_active)` for hierarchical queries
- **Product Images**: `(product_id, is_primary)` for primary image queries

### Full-Text Indexes

- **Products**: Full-text search on name, description, and short_description

## Data Types and Constraints

### String Fields

- **VARCHAR**: Used for short strings with appropriate length limits
- **TEXT**: Used for longer text content like descriptions
- **CHAR**: Used for fixed-length strings like status codes

### Numeric Fields

- **BIGINT**: Used for IDs and large integers
- **INT**: Used for quantities and small integers
- **DECIMAL**: Used for prices and measurements with precision

### Date/Time Fields

- **TIMESTAMP**: Used for created_at and updated_at fields
- **DATE**: Used for date-only fields like date_of_birth

### Boolean Fields

- **BOOLEAN**: Used for true/false flags with NOT NULL DEFAULT constraints

### JSON Fields

- **JSON**: Used for flexible data storage like audit logs

## Relationships

### One-to-One Relationships

- `users` ↔ `user_profiles`

### One-to-Many Relationships

- `categories` → `categories` (self-referencing for hierarchy)
- `categories` → `products`
- `products` → `product_images`
- `products` → `product_specifications`
- `users` → `jwt_tokens`
- `users` → `audit_logs`

### Many-to-Many Relationships

Currently none, but can be added for:

- Product tags
- User roles and permissions
- Product variants

## Performance Optimizations

### Query Optimization

- Proper indexing on frequently queried columns
- Composite indexes for multi-column queries
- Full-text indexes for search functionality
- Foreign key constraints for data integrity

### Storage Optimization

- Appropriate data types to minimize storage
- NULL constraints where appropriate
- Default values to reduce NULL storage

### Connection Optimization

- Connection pooling configuration
- Query timeout settings
- Transaction isolation levels

## Security Considerations

### Data Protection

- Password hashing (handled by Django)
- Sensitive data encryption
- Audit logging for data changes

### Access Control

- Database user with minimal required permissions
- Connection encryption (SSL/TLS)
- Regular security updates

### Backup Strategy

- Regular automated backups
- Point-in-time recovery capability
- Backup encryption and off-site storage

## Migration Strategy

### Django Migrations

```python
# Example migration file structure
class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                # Field definitions
            ],
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'is_active'], name='idx_product_category_active'),
        ),
    ]
```

### Database Migrations

- Use Django's migration system for schema changes
- Test migrations on staging environment first
- Backup database before applying migrations
- Monitor performance after migration

## Monitoring and Maintenance

### Performance Monitoring

- Query performance analysis
- Index usage monitoring
- Connection pool monitoring
- Storage usage tracking

### Maintenance Tasks

- Regular index optimization
- Table statistics updates
- Log file rotation
- Backup verification

### Health Checks

- Database connectivity tests
- Query response time monitoring
- Storage space monitoring
- Connection pool health checks
