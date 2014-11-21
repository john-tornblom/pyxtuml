
CREATE TABLE DIM_WAY (
	     Way_ID	UNIQUE_ID,
	     positionX	REAL,
	     positionY	REAL,
	     edge_elementId	UNIQUE_ID,
	     polyLine_elementId	UNIQUE_ID,
	     previous_Way_ID	UNIQUE_ID );
CREATE TABLE DIM_TEL (
	     text	STRING,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_SSME (
	     typeInfo	STRING,
	     Smb_ID	UNIQUE_ID );
CREATE TABLE DIM_SMB (
	     Smb_ID	UNIQUE_ID,
	     presentation	STRING );
CREATE TABLE DIM_REF (
	     elementId	UNIQUE_ID,
	     Leaf_elementId	UNIQUE_ID,
	     isIndividualRepresentation	BOOLEAN );
CREATE TABLE DIM_PRP (
	     Property_ID	INTEGER,
	     key	STRING,
	     value	STRING,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_PLN (
	     closed	BOOLEAN,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_LEL (
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_IMG (
	     uri	STRING,
	     mimeType	STRING,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_ND (
	     width	REAL,
	     height	REAL,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_GRP (
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_GE (
	     positionX	REAL,
	     positionY	REAL,
	     elementId	UNIQUE_ID,
	     Smb_ID	UNIQUE_ID );
CREATE TABLE DIM_ED (
	     first_conId	UNIQUE_ID,
	     last_conId	UNIQUE_ID,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_CON (
	     conId	UNIQUE_ID,
	     positionX	REAL,
	     positionY	REAL,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_ELP (
	     centerX	REAL,
	     centerY	REAL,
	     radiusX	REAL,
	     radiusY	REAL,
	     rotation	REAL,
	     startAngle	REAL,
	     endAngle	REAL,
	     elementId	UNIQUE_ID );
CREATE TABLE DIM_ELM (
	     represents	INTEGER );
CREATE TABLE DIM_DLK (
	     Link_ID	UNIQUE_ID,
	     zoom	REAL,
	     viewportX	REAL,
	     viewportY	REAL,
	     container_elementId	UNIQUE_ID,
	     diagram_diagramId	UNIQUE_ID );
CREATE TABLE DIM_ELE (
	     elementId	UNIQUE_ID,
	     isVisible	BOOLEAN,
	     container_elementId	UNIQUE_ID );
CREATE TABLE DIM_DIA (
	     diagramId	UNIQUE_ID,
	     name	STRING,
	     zoom	REAL,
	     viewportX	REAL,
	     viewportY	REAL,
	     Smb_ID	UNIQUE_ID );
CREATE TABLE DIM_CSMB (
	     Smb_ID	UNIQUE_ID,
	     represents	INTEGER );
CREATE TABLE TS_NCS (
	     OOA_Type	INTEGER );
CREATE TABLE TS_CTR (
	     OOA_Type	INTEGER );
CREATE TABLE STY_LCS (
	     Style_ID	UNIQUE_ID,
	     red	INTEGER,
	     green	INTEGER,
	     blue	INTEGER );
CREATE TABLE STY_FS (
	     Style_ID	UNIQUE_ID,
	     font_identifier	STRING );
CREATE TABLE STY_FCS (
	     Style_ID	UNIQUE_ID,
	     red	INTEGER,
	     green	INTEGER,
	     blue	INTEGER );
CREATE TABLE STY_S (
	     Style_ID	UNIQUE_ID,
	     elementId	UNIQUE_ID,
	     diagramId	UNIQUE_ID );
CREATE TABLE GD_SHP (
	     elementId	UNIQUE_ID );
CREATE TABLE GD_NCS (
	     elementId	UNIQUE_ID );
CREATE TABLE GD_MD (
	     diagramId	UNIQUE_ID,
	     Model_Type	INTEGER,
	     OOA_ID	UNIQUE_ID,
	     OOA_Type	INTEGER,
	     UseGlobalPrint	BOOLEAN,
	     PrintMode	BOOLEAN,
	     PrintRows	INTEGER,
	     PrintCols	INTEGER,
	     IsLandscape	BOOLEAN,
	     ZoomFontSize	INTEGER,
	     GridOn	BOOLEAN,
	     SelRectX	INTEGER,
	     SelRectY	INTEGER,
	     SelRectW	INTEGER,
	     SelRectH	INTEGER,
	     represents	INTEGER,
	     current_state	INTEGER,
	     version	STRING,
	     represents_path	STRING );
CREATE TABLE GD_LS (
	     elementId	UNIQUE_ID,
	     conn_elementId	UNIQUE_ID,
	     Previous_elementId	UNIQUE_ID,
	     start_Way_ID	UNIQUE_ID,
	     end_Way_ID	UNIQUE_ID );
CREATE TABLE GD_LAY (
	     Layer_Name	STRING,
	     visible	BOOLEAN,
	     diagramId	UNIQUE_ID );
CREATE TABLE GD_GLAY (
	     Layer_Name	STRING,
	     elementId	UNIQUE_ID );
CREATE TABLE GD_GE (
	     elementId	UNIQUE_ID,
	     diagramId	UNIQUE_ID,
	     OOA_ID	UNIQUE_ID,
	     OOA_Type	INTEGER,
	     represents	INTEGER,
	     represents_path	STRING );
CREATE TABLE GD_CTXT (
	     elementId	UNIQUE_ID,
	     conn_elementId	UNIQUE_ID,
	     end	INTEGER,
	     deltaX	REAL,
	     deltaY	REAL );
CREATE TABLE GD_EIS (
	     diagramId	UNIQUE_ID,
	     elementId	UNIQUE_ID );
CREATE TABLE GD_CTR (
	     elementId	UNIQUE_ID );
CREATE TABLE GD_CON (
	     elementId	UNIQUE_ID,
	     Assoc_elementId	UNIQUE_ID );
CREATE TABLE GD_AOS (
	     conId	UNIQUE_ID,
	     elementId	UNIQUE_ID );

CREATE ROP REF_ID R311 FROM MC 	DIM_CON 	( elementId )
		         TO 1  	DIM_GE 	( elementId );
CREATE ROP REF_ID R310 FROM MC 	DIM_PRP 	( elementId )
		         TO 1  	DIM_ELE 	( elementId );
CREATE ROP REF_ID R307 FROM MC 	DIM_ELE 	( container_elementId )
		         TO 1C  DIM_GE 	( elementId );
CREATE ROP REF_ID R308 FROM MC 	DIM_REF 	( Leaf_elementId )
		         TO 1  	DIM_ELE 	( elementId );
CREATE ROP REF_ID R309 FROM MC 	DIM_DLK 	( container_elementId )
		         TO 1  	DIM_GE 	( elementId );
CREATE ROP REF_ID R301 FROM 1C 	DIM_ND 	( elementId )
		     TO 1  	DIM_GE 	( elementId );
CREATE ROP REF_ID R301 FROM 1C 	DIM_ED 	( elementId )
		     TO 1  	DIM_GE 	( elementId );
CREATE ROP REF_ID R302 FROM 1C 	DIM_GE 	( elementId )
		     TO 1  	DIM_ELE 	( elementId );
CREATE ROP REF_ID R302 FROM 1C 	DIM_LEL 	( elementId )
		     TO 1  	DIM_ELE 	( elementId );
CREATE ROP REF_ID R302 FROM 1C 	DIM_REF 	( elementId )
		     TO 1  	DIM_ELE 	( elementId );
CREATE ROP REF_ID R316 FROM MC 	DIM_DLK 	( diagram_diagramId )
		         TO 1  	DIM_DIA 	( diagramId );
CREATE ROP REF_ID R317 FROM 1C 	DIM_DIA 	( Smb_ID )
		         TO 1C  DIM_SMB 	( Smb_ID );
CREATE ROP REF_ID R312 FROM 1C 	DIM_GE 	( Smb_ID )
		         TO 1C  DIM_SMB 	( Smb_ID );
CREATE ROP REF_ID R313 FROM 1C 	DIM_SSME 	( Smb_ID )
		     TO 1  	DIM_SMB 	( Smb_ID );
CREATE ROP REF_ID R313 FROM 1C 	DIM_CSMB 	( Smb_ID )
		     TO 1  	DIM_SMB 	( Smb_ID );
CREATE ROP REF_ID R319 FROM M 	DIM_WAY 	( edge_elementId )
		         TO 1  	DIM_ED 	( elementId );
CREATE ROP REF_ID R315 FROM MC 	DIM_CSMB 	( represents )
		         TO 1  	DIM_ELM 	( represents );
CREATE ROP REF_ID R320 FROM MC 	DIM_ED 	( first_conId )
		         TO 1C  DIM_CON 	( conId );
CREATE ROP REF_ID R305 FROM 1C 	DIM_IMG 	( elementId )
		     TO 1  	DIM_LEL 	( elementId );
CREATE ROP REF_ID R305 FROM 1C 	DIM_TEL 	( elementId )
		     TO 1  	DIM_LEL 	( elementId );
CREATE ROP REF_ID R305 FROM 1C 	DIM_GRP 	( elementId )
		     TO 1  	DIM_LEL 	( elementId );
CREATE ROP REF_ID R306 FROM 1C 	DIM_PLN 	( elementId )
		     TO 1  	DIM_GRP 	( elementId );
CREATE ROP REF_ID R306 FROM 1C 	DIM_ELP 	( elementId )
		     TO 1  	DIM_GRP 	( elementId );
CREATE ROP REF_ID R323 FROM M 	DIM_WAY 	( polyLine_elementId )
		         TO 1C  DIM_PLN 	( elementId );
CREATE ROP REF_ID R321 FROM MC 	DIM_ED 	( last_conId )
		         TO 1C  DIM_CON 	( conId );
CREATE ROP REF_ID R324 FROM 1C 	DIM_WAY 	( previous_Way_ID )  PHRASE 'follows'
		         TO 1C  DIM_WAY 	( Way_ID )  PHRASE 'precedes';
CREATE ROP REF_ID R400 FROM 1C 	STY_FCS 	( Style_ID )
		     TO 1  	STY_S 	( Style_ID );
CREATE ROP REF_ID R400 FROM 1C 	STY_LCS 	( Style_ID )
		     TO 1  	STY_S 	( Style_ID );
CREATE ROP REF_ID R400 FROM 1C 	STY_FS 	( Style_ID )
		     TO 1  	STY_S 	( Style_ID );
CREATE ROP REF_ID R401 FROM MC 	STY_S 	( elementId )
		         TO 1  	GD_GE 	( elementId );
CREATE ROP REF_ID R402 FROM MC 	STY_S 	( diagramId )
		         TO 1  	GD_MD 	( diagramId );
CREATE ROP REF_ID R1 FROM MC 	GD_GE 	( diagramId )
		         TO 1C  GD_MD 	( diagramId );
CREATE ROP REF_ID R2 FROM 1C 	GD_SHP 	( elementId )
		     TO 1  	GD_GE 	( elementId );
CREATE ROP REF_ID R2 FROM 1C 	GD_CON 	( elementId )
		     TO 1  	GD_GE 	( elementId );
CREATE ROP REF_ID R5 FROM 1C 	GD_CON 	( Assoc_elementId )
		         TO 1C  GD_LS 	( elementId );
CREATE ROP REF_ID R7 FROM 1C 	GD_LS 	( Previous_elementId )  PHRASE 'follows'
		         TO 1C  GD_LS 	( elementId )  PHRASE 'precedes';
CREATE ROP REF_ID R18 FROM 1C 	GD_MD 	( diagramId )
		     TO 1  	DIM_DIA 	( diagramId );
CREATE ROP REF_ID R20 FROM 1C 	GD_CON 	( elementId )
		     TO 1  	DIM_ED 	( elementId );
CREATE ROP REF_ID R21 FROM 1C 	GD_LS 	( start_Way_ID )
		         TO 1  	DIM_WAY 	( Way_ID );
CREATE ROP REF_ID R22 FROM 1C 	GD_LS 	( end_Way_ID )
		         TO 1  	DIM_WAY 	( Way_ID );
CREATE ROP REF_ID R23 FROM 1C 	GD_GE 	( elementId )
		         TO 1  	DIM_GE 	( elementId );
CREATE ROP REF_ID R8 FROM M 	GD_CTXT 	( conn_elementId )
		         TO 1C  GD_CON 	( elementId );
CREATE ROP REF_ID R6 FROM M 	GD_LS 	( conn_elementId )
		         TO 1  	GD_CON 	( elementId );
CREATE ROP REF_ID R26 FROM 1C 	GD_AOS 	( conId )
		         TO 1  	DIM_CON 	( conId );
CREATE ROP REF_ID R26 FROM MC 	GD_AOS 	( elementId )
		         TO 1  	GD_LS 	( elementId );
CREATE ROP REF_ID R27 FROM 1C 	GD_CTXT 	( conn_elementId )
		         TO 1C  GD_SHP 	( elementId );
CREATE ROP REF_ID R19 FROM 1C 	GD_SHP 	( elementId )
		     TO 1  	DIM_ND 	( elementId );
CREATE ROP REF_ID R19 FROM 1C 	GD_CTXT 	( elementId )
		     TO 1  	DIM_ND 	( elementId );
CREATE ROP REF_ID R28 FROM 1C 	GD_NCS 	( elementId )
		     TO 1  	GD_SHP 	( elementId );
CREATE ROP REF_ID R28 FROM 1C 	GD_CTR 	( elementId )
		     TO 1  	GD_SHP 	( elementId );
CREATE ROP REF_ID R32 FROM MC 	GD_EIS 	( diagramId )
		         TO 1  	GD_MD 	( diagramId );
CREATE ROP REF_ID R32 FROM 1C 	GD_EIS 	( elementId )
		         TO 1  	GD_GE 	( elementId );
CREATE ROP REF_ID R34 FROM MC 	GD_LAY 	( diagramId )
		         TO 1  	GD_MD 	( diagramId );
CREATE ROP REF_ID R35 FROM MC 	GD_GLAY 	( Layer_Name )
		         TO 1  	GD_LAY 	( Layer_Name );
CREATE ROP REF_ID R35 FROM M 	GD_GLAY 	( elementId )
		         TO 1  	GD_GE 	( elementId );

