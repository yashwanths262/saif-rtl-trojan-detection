`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 02.09.2026 23:43:33
// Design Name: 
// Module Name: trojan_alu1
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module golden_alu1 (
    input  wire       clk,
    input  wire       reset,
    input  wire       enable,

    input  wire [7:0] A,
    input  wire [7:0] B,
    input  wire [1:0] op,

    output reg  [7:0] result
);

    reg [7:0] alu_result;

    // Combinational ALU logic
    always @(*) begin

        case (op)

            2'b00:
                alu_result = A + B;

            2'b01:
                alu_result = A - B;

            2'b10:
                alu_result = A & B;

            2'b11:
                alu_result = A | B;

            default:
                alu_result = 8'b0;

        endcase

    end

    // Registered output
    always @(posedge clk) begin

        if (reset)
            result <= 8'b0;

        else if (enable)
            result <= alu_result;

    end

endmodule
