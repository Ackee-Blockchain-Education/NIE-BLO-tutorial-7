// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract NumberMagic {
    int256 private keypad;
    bool private locked = true;

    modifier flagMagic() {
        _;
        updateHiddenFlag();
    }

    function multiply(int256 value) public flagMagic {
        unchecked {
            keypad *= value;
        }
    }

    function divide(int256 value) public flagMagic {
        require(value != 0, "Division by zero");
        keypad /= value;
    }

    function xor(int256 xorValue) public flagMagic {
        keypad ^= xorValue;
    }

    function isLocked() public view returns (bool) {
        return locked;
    }

    function getKeypadState() public view returns (int256) {
        return keypad;
    }

    function updateHiddenFlag() internal {
        // prettier-ignore
        locked = !(
               keypad < 0
            && keypad % 2 == 0
            && keypad % 3 == 0
            && keypad % 5 == 0
            && keypad % 7 == 0
            && keypad % 11 == 0
        );
    }
}
