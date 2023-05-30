# Shopless - Customers API

### API Description
Shopless's API is a data transfer tool that facilitates the exchange of information between internal and external systems. This API is used for handling customer data as it generates a unique identifier for each newly added customer. The identifier is returned as part of the response and can be used to access and manage customer data within Shopless's systems.

### Required headers
| Header        | Value                            |
|---------------|----------------------------------|
| Content-Type  | application/json                 |
| Authorization | 5276E111BCFF4E32AD91062A6E45972F |


### HTTP Methods
GET / POST / PUT / DELETE

### Schema

````
{
  "type": "object",
  "properties": {
    "firstName": {
      "type": "string"
    },
    "lastName": {
      "type": "string"
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "address": {
      "type": "string"
    }
  },
  "required": [
    "firstName",
    "lastName",
    "email",
    "address"
  ]
}

````

### Example Payload

#### Customers 

````
{
  "firstName": "Simon",
  "lastName": "Jones",
  "email": "simon.jones@gmail.com",
  "address": "The Cottage, Liverpool, Merseyside, L18 4DD"
}
````


### GET
| Response | Message               | Description                       | 
|----------|-----------------------|-----------------------------------|
| 200      | OK                    | Successful                        |
| 401      | Unauthorized          | Unauthorized                      |
| 404      | Not Found             | No customers found                |
| 404      | Not Found             | Customer with name {id} not found |
| 500      | Internal Server Error | An error occurred on the server   |


### POST
| Response | Message               | Description                     | 
|----------|-----------------------|---------------------------------|
| 201      | Created               | Customer created successfully   |
| 400      | Bad Request           | Invalid Data                    |
| 401      | Unauthorized          | Unauthorized                    |
| 500      | Internal Server Error | An error occurred on the server |

### PUT
| Response  | Message               | Description                       | 
|-----------|-----------------------|-----------------------------------|
| 200       | OK                    | Customer updated successfully     |
| 400       | Bad Request           | Invalid Data                      |
| 401       | Unauthorized          | Unauthorized                      |
| 404       | Not Found             | Customer with name {id} not found |
| 500       | Internal Server Error | An error occurred on the server   |

### DELETE
| Response  | Message               | Description                      | 
|-----------|-----------------------|----------------------------------|
| 200       | OK                    | Customer deleted successfully    |
| 401       | Unauthorized          | Unauthorized                     |
| 404       | Not Found             | Customer with {id} not found     |
| 500       | Internal Server Error | Error deleting customer: {error} |








