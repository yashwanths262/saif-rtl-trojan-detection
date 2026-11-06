`timescale 1ns / 1ps

module golden_tb;

    reg clk;
    reg reset;
    reg enable;

    reg [7:0] A;
    reg [7:0] B;
    reg [1:0] op;

    wire [7:0] result;


    // =================================================
    // Golden ALU
    // =================================================

    golden_alu1 uut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .A(A),
        .B(B),
        .op(op),
        .result(result)
    );


    // =================================================
    // Clock
    // =================================================

    initial begin
        clk = 1'b0;

        forever #5 clk = ~clk;
    end


    // =================================================
    // Test stimulus
    // =================================================

integer i;
integer seed;

initial begin

    seed = 1009;
   

    reset  = 1'b1;
    enable = 1'b0;

    A  = 8'h00;
    B  = 8'h00;
    op = 2'b00;

    #20;

    reset  = 1'b0;
    enable = 1'b1;

    for (i = 0; i < 50; i = i + 1) begin

        A  = $random(seed);
        B  = $random(seed);
        op = $random(seed);

        #10;

    end

    enable = 1'b0;

    #20;

    $finish;

end

endmodule