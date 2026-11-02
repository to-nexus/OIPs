// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.22;

import {IERC20, IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import {Test} from "forge-std/Test.sol";

/// @notice ORC-20 token-side test cases, run against the token returned by `token()`.
abstract contract ORC20Conformance is Test {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    address internal immutable A = makeAddr("orc20.A");
    address internal immutable B = makeAddr("orc20.B");
    address internal immutable S = makeAddr("orc20.S");

    /// @notice Returns the token under test.
    function token() internal view virtual returns (IERC20Metadata);

    /// @notice Sets the raw balance of `to` to `amount`, adjusting the total supply.
    function fund(address to, uint256 amount) internal {
        deal(address(token()), to, amount, true);
    }

    /// @notice Selects a fork from `<prefix>_URL` and optional `<prefix>_BLOCK`, or skips the suite without a URL.
    /// @dev A historical block needs an archive endpoint.
    function forkFromEnv(string memory prefix, uint256 chainId) internal {
        string memory url = vm.envOr(string.concat(prefix, "_URL"), string(""));
        vm.skip(bytes(url).length == 0);
        uint256 blockNumber = vm.envOr(string.concat(prefix, "_BLOCK"), uint256(0));
        if (blockNumber == 0) vm.createSelectFork(url);
        else vm.createSelectFork(url, blockNumber);
        assertEq(block.chainid, chainId);
    }

    /// @notice Calls the token as `from` and requires an ABI-encoded `true` on success.
    function callOk(address from, bytes memory data) internal {
        vm.prank(from);
        (bool ok, bytes memory ret) = address(token()).call(data);
        assertTrue(ok, "call reverted");
        assertEq(ret.length, 32, "return is not one ABI word");
        assertTrue(abi.decode(ret, (bool)), "returned false");
    }

    /// @notice Calls the token as `from` and returns whether the call succeeded.
    function callRaw(address from, bytes memory data) internal returns (bool ok) {
        vm.prank(from);
        (ok,) = address(token()).call(data);
    }

    function test_metadataTypesWithoutPrivilege() public {
        address t = address(token());
        vm.startPrank(makeAddr("orc20.anyone"));
        (bool ok1, bytes memory n) = t.staticcall(abi.encodeCall(IERC20Metadata.name, ()));
        (bool ok2, bytes memory s) = t.staticcall(abi.encodeCall(IERC20Metadata.symbol, ()));
        (bool ok3, bytes memory d) = t.staticcall(abi.encodeCall(IERC20Metadata.decimals, ()));
        vm.stopPrank();
        assertTrue(ok1 && ok2 && ok3, "metadata call failed");
        // abi.decode reverts unless the data is a valid string or an in-range uint8.
        // Nonempty strings are ORC-20's SHOULD recommendation for display.
        assertGt(bytes(abi.decode(n, (string))).length, 0);
        assertGt(bytes(abi.decode(s, (string))).length, 0);
        assertEq(d.length, 32);
        abi.decode(d, (uint8));
    }

    function test_transfer() public {
        fund(A, 100);
        uint256 supply = token().totalSupply();
        vm.expectEmit(address(token()));
        emit Transfer(A, B, 25);
        callOk(A, abi.encodeCall(IERC20.transfer, (B, 25)));
        assertEq(token().balanceOf(A), 75);
        assertEq(token().balanceOf(B), 25);
        assertEq(token().totalSupply(), supply);
    }

    function test_zeroValueTransfer() public {
        fund(A, 100);
        vm.expectEmit(address(token()));
        emit Transfer(A, B, 0);
        callOk(A, abi.encodeCall(IERC20.transfer, (B, 0)));
        assertEq(token().balanceOf(A), 100);
        assertEq(token().balanceOf(B), 0);
    }

    function test_approveReplacesAllowance() public {
        vm.expectEmit(address(token()));
        emit Approval(A, S, 40);
        callOk(A, abi.encodeCall(IERC20.approve, (S, 40)));
        vm.expectEmit(address(token()));
        emit Approval(A, S, 10);
        callOk(A, abi.encodeCall(IERC20.approve, (S, 10)));
        assertEq(token().allowance(A, S), 10);
    }

    function test_transferFromFiniteAllowance() public {
        fund(A, 100);
        callOk(A, abi.encodeCall(IERC20.approve, (S, 40)));
        callOk(S, abi.encodeCall(IERC20.transferFrom, (A, B, 15)));
        assertEq(token().balanceOf(A), 85);
        assertEq(token().balanceOf(B), 15);
        assertEq(token().allowance(A, S), 25);
    }

    function test_rejectsInsufficientBalance() public {
        fund(A, 10);
        uint256 supply = token().totalSupply();
        assertFalse(callRaw(A, abi.encodeCall(IERC20.transfer, (B, 11))));
        assertEq(token().balanceOf(A), 10);
        assertEq(token().balanceOf(B), 0);
        assertEq(token().totalSupply(), supply);
    }

    function test_rejectsInsufficientAllowance() public {
        fund(A, 100);
        callOk(A, abi.encodeCall(IERC20.approve, (S, 5)));
        assertFalse(callRaw(S, abi.encodeCall(IERC20.transferFrom, (A, B, 6))));
        assertEq(token().balanceOf(A), 100);
        assertEq(token().balanceOf(B), 0);
        assertEq(token().allowance(A, S), 5);
    }
}
