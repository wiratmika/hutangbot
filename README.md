# Hutangbot

Might be renamed in the future as Debtwise(r). Make debt wisely!

## Usage instruction

Note that all amount has to be in positive number greater than zero and without punctuation.

### Make a debt (i.e. you owe someone)

```
/hutang [user] [amount]
e.g.
/hutang @John Doe 69000
```

### Pay a debt

```
/bayar [user] [amount]
e.g.
/bayar @John Doe 69000

or

/bayar [transaction_id]
e.g.
/bayar c2d3r4
```

### Make a piutang (i.e. somone owe you)

```
/piutang [user] [amount]
e.g.
/piutang @John Doe 69000
```

### See net list of your debt (who and how much you owe, and vice versa)

```
/listhutang
```

### See list of all of your transactions (including those made by others)

```
/listtransaksi
```

### Delete a transaction (in case you made a mistake)

```
/hapus [transaction ID]
e.g.
/hapus d92dw
```

## Future development

- Webhook to notify the other user
