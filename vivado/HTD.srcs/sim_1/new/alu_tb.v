`timescale 1ns / 1ps

module alu_tb;

    reg clk;
    reg reset;
    reg enable;

    reg [7:0] A;
    reg [7:0] B;
    reg [1:0] op;

    wire [7:0] golden_result;
    wire [7:0] trojan_result;


    // =================================================
    // Golden ALU
    // =================================================

    golden_alu1 golden_uut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .A(A),
        .B(B),
        .op(op),
        .result(golden_result)
    );


    // =================================================
    // Trojan ALU
    // =================================================

    trojan_alu1 trojan_uut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .A(A),
        .B(B),
        .op(op),
        .result(trojan_result)
    );


    // =================================================
    // Clock generation
    // 10 ns clock period
    // =================================================

    initial begin

        clk = 1'b0;

        forever #5 clk = ~clk;

    end


    // =================================================
    // Test sequence
    // =================================================

    initial begin

        // -------------------------------------------------
        // Initial values
        // -------------------------------------------------

        reset  = 1'b1;
        enable = 1'b0;

        A  = 8'h00;
        B  = 8'h00;
        op = 2'b00;


        // -------------------------------------------------
        // Reset
        // -------------------------------------------------

        #20;

        reset  = 1'b0;
        enable = 1'b1;


        // =================================================
        // NORMAL OPERATION
        // =================================================

        // Addition
        A = 8'h12;
        B = 8'h34;
        op = 2'b00;

        #10;


        // Subtraction
        A = 8'h55;
        B = 8'h0F;
        op = 2'b01;

        #10;


        // AND
        A = 8'hAA;
        B = 8'h33;
        op = 2'b10;

        #10;


        // OR
        A = 8'hF0;
        B = 8'h0F;
        op = 2'b11;

        #10;


        // Addition
        A = 8'h21;
        B = 8'h17;
        op = 2'b00;

        #10;


        // Subtraction
        A = 8'h80;
        B = 8'h11;
        op = 2'b01;

        #10;


        // AND
        A = 8'h3C;
        B = 8'h55;
        op = 2'b10;

        #10;


        // OR
        A = 8'h7A;
        B = 8'h81;
        op = 2'b11;

        #10;


        // Addition
        A = 8'h19;
        B = 8'h27;
        op = 2'b00;

        #10;


        // Subtraction
        A = 8'hFE;
        B = 8'h11;
        op = 2'b01;

        #10;


        // AND
        A = 8'hC3;
        B = 8'h5A;
        op = 2'b10;

        #10;


        // OR
        A = 8'h96;
        B = 8'h69;
        op = 2'b11;

        #10;


        // =================================================
        // TROJAN ACTIVATION
        // =================================================

        // Rare trigger values
        A = 8'hA5;
        B = 8'h3C;
        op = 2'b11;
        enable = 1'b1;


        // Hold trigger long enough for
        // internal_counter to reach 1111
        #60;


        // Keep trigger values stable for a little longer
        #20;


        // Disable circuit
        enable = 1'b0;

        #20;


        // Finish simulation
        $finish;

    end

endmodule