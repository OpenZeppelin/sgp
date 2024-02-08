# Changelog

- [0.0.4](#004)

## 0.0.4

### [Fix incorrect state mutability identification](https://github.com/OpenZeppelin/sgp/pull/9)

This PR fixed incorrect state mutability identification for the various structures, such as:

**`const` state mutability for the state variable declaration**

```solidity
contract Example {
    uint256 constant x = 1;
}
```

**`payable` state mutability for the function return parameter variable declaration**

```solidity
function test() public returns(address payable) {}
```

Now, these cases are handled correctly after the bug in the version `0.0.3`.

### [CHANGELOG.md](/CHANGELOG.md) added
